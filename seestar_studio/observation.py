"""Connection-bound, event-driven observation; no global/default telescope.

SeestarPy 0.8.0 wire commands and outer-event semantics are preserved. An ACK
never proves completion. No setting writes, retries, or automatic reconnection
of a sequence. The read-only viewer remains responsible for ongoing telemetry.
"""
from collections import deque
from dataclasses import dataclass, field
import threading
import time
from .i18n import source as ui_text

ACTIVE = {'start', 'working'}
TERMINAL = {'complete', 'fail', 'cancel'}
EVENTS = {'View', 'ScopeGoto', 'AutoGoto', 'PlateSolve', 'AutoFocus', 'Stack',
          'ContinuousExposure', 'ScopeHome', 'ScopeMoveToHorizon'}
LABELS = {
    'Idle': ui_text('ctl_idle'), 'TargetSelected': ui_text('ctl_selected'),
    'GoToRequested': ui_text('ctl_requested'), 'Slewing': ui_text('ctl_slewing'),
    'PlateSolving': ui_text('ctl_solving'), 'TargetAcquired': ui_text('ctl_acquired'),
    'Autofocusing': ui_text('ctl_focusing'), 'ReadyToStack': ui_text('ctl_ready'),
    'StartingStack': ui_text('ctl_start_stack'), 'Stacking': ui_text('ctl_stacking'),
    'Completed': ui_text('ctl_completed'), 'Failed': ui_text('ctl_failed'),
    'Cancelled': ui_text('ctl_cancelled'), 'Unknown': ui_text('ctl_unknown'),
    'Sent': ui_text('ctl_sent'), 'Accepted': ui_text('ctl_accepted'),
    'Started': ui_text('ctl_started'),
}


def outer(frame):
    return 'page' not in frame and ('route' in frame or 'lapse_ms' in frame)


def read_state(transport):
    """Read back actual state, including idle devices with an empty View."""
    app = transport.send({'method': 'iscope_get_app_state'})
    device = transport.send({'method': 'get_device_state', 'params': {
        'keys': ['device', 'mount', 'camera', 'focuser', 'setting']}})
    if any(not isinstance(r, dict) or r.get('code') != 0 or
           not isinstance(r.get('result'), dict) for r in (app, device)):
        raise ConnectionError('Status read rejected')
    d = device['result']; view = app['result'].get('View') or {}
    if not isinstance(view, dict): raise ValueError('Invalid View')
    mount = d.get('mount') or {}; settings = d.get('setting') or {}
    return dict(view_mode=view.get('mode'), view_stage=view.get('stage'),
                view_state=view.get('state'), view=view,
                parked=mount.get('close'), equ_mode=mount.get('equ_mode'),
                move_type=mount.get('move_type'), tracking=mount.get('tracking'),
                camera_ready=bool(d.get('camera')), has_focuser=bool(d.get('focuser')),
                focuser_state=(d.get('focuser') or {}).get('state'),
                auto_af=settings.get('auto_af'), stack_after_goto=settings.get('stack_after_goto'))


@dataclass
class Observation:
    """Pure transition reducer; only new events from this command's connection."""
    state: str = 'Idle'
    solved: bool = False
    acquired: bool = False
    focused: bool = False
    focus_seen: bool = False
    stack_seen: bool = False
    failure: str = ''
    history: list = field(default_factory=list)

    def transition(self, state):
        if self.state != state:
            self.state = state
            self.history.append(state)
            self.history[:] = self.history[-32:]

    def event(self, frame):
        name, state = frame.get('Event'), frame.get('state')
        if self.state in ('Failed', 'Cancelled', 'Unknown'): return
        if name not in EVENTS: return
        # A failed sub-step is enough to prevent follow-on commands. Success,
        # unlike failure, requires the operation's authoritative outer frame.
        if name in ('AutoGoto', 'PlateSolve', 'AutoFocus', 'Stack', 'ScopeGoto') and state == 'fail':
            self.failure = (ui_text('ctl_no_stars') if frame.get('code') == 279 else
                            ui_text('ctl_solve_failed') if name == 'PlateSolve' else
                            ui_text('ctl_operation_failed').format(p0=name, p1=frame.get('code', '—')))
            self.transition('Failed'); return
        if name in ('AutoGoto', 'AutoFocus') and state == 'cancel' and outer(frame):
            self.transition('Cancelled'); return
        if name == 'ScopeGoto' and state in ACTIVE: self.transition('Slewing')
        if name == 'PlateSolve':
            if state in ACTIVE: self.transition('PlateSolving')
            if state == 'complete' and outer(frame): self.solved = True
        if name == 'AutoGoto' and state == 'complete' and outer(frame): self.acquired = True
        if self.acquired and self.solved and not self.focus_seen: self.transition('TargetAcquired')
        if name == 'AutoFocus':
            if state in ACTIVE:
                self.focus_seen = True; self.transition('Autofocusing')
            if state == 'complete' and outer(frame):
                self.focus_seen = True; self.focused = True
        if self.focused and self.acquired and self.solved and not self.stack_seen and self.state != 'StartingStack':
            self.transition('ReadyToStack')
        if name == 'Stack' and state in ACTIVE:
            self.stack_seen = True
            if self.focused and self.acquired and self.solved: self.transition('Stacking')


class Runner:
    """One explicit operation/sequence. Callbacks enqueue only, never send RPCs."""
    def __init__(self, transport, action, command, guard, publish, cancel=None,
                 timeout=300, interval=.5, clock=time.monotonic):
        self.transport, self.action, self.command = transport, action, command
        self.guard, self.publish = guard, publish
        self.cancel = cancel or threading.Event()
        self.timeout, self.interval, self.clock = timeout, interval, clock
        self.machine = Observation()
        self.events = deque(maxlen=512)
        self.event_lock = threading.Lock()
        self.overflow = False
        self.sent = False
        self.stop_sent = False
        self.generation = getattr(transport, 'generation', 0)
        self.owned_stage = None
        self.last_state = None
        self.started_timestamp = None

    def status(self, state, detail=''):
        self.publish(state, detail)

    def check(self):
        self.guard()
        if getattr(self.transport, 'generation', 0) != self.generation:
            raise ConnectionError('Control connection changed')

    def send(self, command):
        self.check()
        response = self.transport.send(command)
        self.check()
        self.status('Sent')
        if not isinstance(response, dict) or response.get('code') != 0 or response.get('error'):
            raise ValueError(ui_text('ctl_rejected'))
        self.status('Accepted')
        return response

    def on_event(self, frame):
        if frame.get('Event') in EVENTS:
            with self.event_lock:
                if len(self.events) == self.events.maxlen: self.overflow = True
                self.events.append(dict(frame))

    def drain(self):
        with self.event_lock:
            frames = list(self.events); self.events.clear()
            if self.overflow: raise ConnectionError('Event queue overflow')
        return frames

    def stop_owned(self):
        # A scoped stop cannot interrupt a replacement view/stack. Read back on
        # the SAME connection first. Never reconnect to send a cancellation.
        if not self.sent or self.stop_sent:
            return
        self.check()
        state = read_state(self.transport); self.check()
        stage = state['view_stage']
        stop_stage = None
        should_stop = self.owned_stage in ('AutoGoto', 'AutoFocus') and stage == self.owned_stage
        if should_stop: stop_stage = self.owned_stage
        # A firmware-initiated stack must not bypass a failed prerequisite in
        # OUR sequence. Manual stack can itself enter Initialise/plate solving.
        if self.action in ('observe', 'stack') and stage == 'Stack':
            should_stop = True; stop_stage = 'Stack'
        if self.action == 'stack' and stage == 'Initialise': should_stop = True
        if should_stop and state['view_state'] in ACTIVE:
            self.stop_sent = True
            response = self.transport.send({'method': 'iscope_stop_view', 'params': {'stage': stop_stage}})
            if response.get('code') != 0: raise ConnectionError('Stop not confirmed')

    def process_events(self, frames, terminal):
        for frame in frames:
            if self.started_timestamp is not None:
                try:
                    if float(frame['Timestamp']) < self.started_timestamp: continue
                except (KeyError, TypeError, ValueError): continue
            self.machine.event(frame)
            if self.machine.state in ('Failed', 'Cancelled'):
                self.stop_owned()
                self.status(self.machine.state, self.machine.failure)
                return True
            if self.action != 'observe' and frame.get('Event') == terminal:
                state = frame.get('state')
                if state == 'fail':
                    self.status('Failed', ui_text('ctl_operation_failed').format(p0=terminal, p1=frame.get('code', '—')))
                    return True
                if state == 'complete' and outer(frame):
                    self.status('Completed'); return True
                if state in ACTIVE:
                    self.status('Stacking' if self.action == 'stack' else 'Started')
                    if self.action in ('preview', 'stack'): return True
                if state == 'cancel' and outer(frame):
                    self.status('Cancelled'); return True
        return False

    def run(self, before):
        t = self.transport
        terminal = {'goto': 'ScopeGoto', 'observe': 'AutoGoto', 'autofocus': 'AutoFocus',
                    'preview': 'ContinuousExposure', 'stack': 'Stack', 'park': 'ScopeHome',
                    'unpark': 'ScopeMoveToHorizon'}.get(self.action)
        if self.action == 'observe':
            if type(before.get('auto_af')) is not bool or type(before.get('stack_after_goto')) is not bool:
                raise ValueError(ui_text('ctl_flags_unknown'))
            if before['stack_after_goto'] and not before['auto_af']:
                raise ValueError(ui_text('ctl_flags_conflict'))
        # Drain previously queued device events before registering this run.
        t.send({'method': 'test_connection'}); self.check()
        t.add_event_handler(self.on_event)
        focus_sent = stack_sent = False
        self.owned_stage = terminal if terminal in ('AutoGoto', 'AutoFocus') else None
        try:
            self.machine.transition('GoToRequested' if self.action in ('goto', 'observe') else 'Idle')
            self.status(self.machine.state)
            reply = self.send(self.command); self.sent = True
            try: self.started_timestamp = float(reply['Timestamp'])
            except (KeyError, TypeError, ValueError): pass
            deadline = self.clock() + self.timeout
            while self.clock() < deadline:
                self.check()
                if self.cancel.is_set():
                    self.stop_owned()
                    self.status('Cancelled', ui_text('ctl_cancel_note'))
                    return
                t.send({'method': 'test_connection'}); self.check()
                if self.process_events(self.drain(), terminal): return
                state = read_state(t); self.check(); self.last_state = state
                # Status replies also pump events. A failure received during a
                # read must veto follow-on commands in this same iteration.
                if self.process_events(self.drain(), terminal): return
                stage, active = state['view_stage'], state['view_state'] in ACTIVE
                if self.action == 'observe':
                    m = self.machine
                    # Firmware can auto-start AF/stack; actual stage is additional
                    # evidence of START, never substitute for successful solving/AF.
                    if stage == 'AutoFocus' and active:
                        m.event({'Event': 'AutoFocus', 'state': 'working'})
                        if m.acquired: self.owned_stage = 'AutoFocus'
                    if stage == 'Stack' and active:
                        m.event({'Event': 'Stack', 'state': 'working'})
                    self.status(m.state)
                    if m.state == 'Stacking': return
                    if m.stack_seen and not m.focused:
                        self.stop_owned()
                        self.status('Unknown', ui_text('ctl_unverified_stack')); return
                    if m.acquired and m.solved and stage == 'ContinuousExposure' and active:
                        if not m.focus_seen and not before['auto_af'] and not focus_sent:
                            focus_sent = True; self.owned_stage = 'AutoFocus'
                            self.send({'method': 'start_auto_focuse'})
                        elif m.focused and not before['stack_after_goto'] and not stack_sent:
                            stack_sent = True; self.owned_stage = None
                            m.transition('StartingStack'); self.status('StartingStack')
                            self.send({'method': 'iscope_start_stack', 'params': {'restart': False}})
                elif self.action == 'preview' and stage == 'ContinuousExposure' and active and state['view_mode'] == 'star':
                    self.status('Started'); return
                elif self.action == 'stack' and stage == 'Stack' and active:
                    self.status('Stacking'); return
                elif self.action == 'stop_view' and not active:
                    self.status('Completed'); return
                elif self.action == 'stop_stack' and stage == 'ContinuousExposure' and active:
                    self.status('Completed'); return
                if not terminal and self.action not in ('stop_view', 'stop_stack'):
                    return  # Setting ACK only; never call it an operation completion.
                self.cancel.wait(self.interval)
            self.stop_owned()
            self.status('Unknown', ui_text('ctl_timeout'))
        finally:
            t.remove_event_handler(self.on_event)
