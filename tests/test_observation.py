"""Simulated protocols based on the 2026-11-07 indoor event shapes.

Successful solving/focus fixtures are simulations, NOT hardware validation.
"""
from dataclasses import replace
import threading
import time
import pytest
from seestar_studio.observation import Observation, Runner, read_state
from seestar_studio.control import ControlService, payload, available, unavailable_reason
from seestar_studio.models import Telemetry
from tests.test_control import FakeTransport, fleet


def event(name, state, **extra):
    return {'Event': name, 'state': state, 'lapse_ms': 10, 'route': ['View'], **extra}


SOLVE = [event('ScopeGoto', 'working'), event('ScopeGoto', 'complete'),
         event('PlateSolve', 'working'), event('PlateSolve', 'complete'), event('AutoGoto', 'complete')]
FOCUS = [event('AutoFocus', 'working'), event('AutoFocus', 'complete')]


class Scripted(FakeTransport):
    def __init__(self, ip='127.0.0.1', auto=False, script=None, reject=None, lost=None):
        super().__init__(ip)
        self.calls = []; self.auto = auto; self.script = list(script or SOLVE)
        self.reject, self.lost = reject, lost
        self.view = {}; self.pending = []; self.started = False
        self.responses = []

    def send(self, command):
        method = command['method']
        if method == 'get_device_state':
            response = super().send(command)
            response['result']['setting'] = {'auto_af': self.auto, 'stack_after_goto': self.auto}
            return response
        if method == 'iscope_get_app_state': return {'code': 0, 'result': {'View': dict(self.view)}}
        if method == 'test_connection':
            if self.started and self.pending:
                f = self.pending.pop(0)
                if f == 'disconnect': raise ConnectionError('Simulated disconnect')
                name, state = f['Event'], f['state']
                if name in ('AutoFocus', 'Stack', 'AutoGoto') and state in ('working', 'start'):
                    self.view = {'mode': 'star', 'stage': name, 'state': 'working'}
                if name in ('AutoGoto', 'AutoFocus') and state == 'complete':
                    self.view = {'mode': 'star', 'stage': 'ContinuousExposure', 'state': 'working'}
                for handler in list(self.handlers): handler(f)
            return {'code': 0}
        if method == 'get_wheel_position': return {'code': 0, 'result': 1}
        self.calls.append((self.ip, command))
        if method == self.lost: raise ConnectionError('Simulated lost reply')
        if method == self.reject: return {'code': 203}
        if method == 'iscope_start_view':
            self.started = True
            self.view = {'mode': 'star', 'stage': 'AutoGoto', 'state': 'working'}
            self.pending.extend(self.script)
        elif method == 'start_auto_focuse': self.pending.extend(FOCUS)
        elif method == 'iscope_start_stack': self.pending.append(event('Stack', 'working'))
        elif method == 'iscope_stop_view':
            self.view = {'mode': 'star', 'stage': 'ContinuousExposure', 'state': 'working'}
            self.pending.clear()
        return {'code': 0}


def run(transport, **kwargs):
    messages = []
    command = payload('observe', {'ra': 180, 'dec': 40}, fleet()['1'][1])
    r = Runner(transport, 'observe', command, lambda: None,
               lambda state, detail='': messages.append((state, detail)),
               interval=.001, timeout=.15, **kwargs)
    r.run(read_state(transport))
    return r, messages


def mutations(t): return [c['method'] for _, c in t.calls]


def test_full_sequence_manual_followups_only_after_success():
    t = Scripted(); r, messages = run(t)
    assert messages[-1][0] == 'Stacking'
    assert mutations(t) == ['iscope_start_view', 'start_auto_focuse', 'iscope_start_stack']
    assert r.machine.history == ['GoToRequested', 'Slewing', 'PlateSolving', 'TargetAcquired',
                                 'Autofocusing', 'ReadyToStack', 'StartingStack', 'Stacking']
    assert t.calls[-1][1]['params'] == {'restart': False}


def test_firmware_automatic_focus_before_goto_terminal_no_duplicate_commands():
    t = Scripted(auto=True, script=SOLVE[:-1] + FOCUS + SOLVE[-1:] + [event('Stack', 'working')])
    r, messages = run(t)
    assert messages[-1][0] == 'Stacking'
    assert mutations(t) == ['iscope_start_view']


@pytest.mark.parametrize('failure', ['PlateSolve', 'AutoFocus'])
def test_failure_never_follows_on_and_scoped_stop_of_own_operation(failure):
    script = SOLVE[:3] + [event('PlateSolve', 'fail', page='preview', code=251), event('AutoFocus', 'working')]
    if failure == 'AutoFocus': script = SOLVE + [event('AutoFocus', 'working'), event('AutoFocus', 'fail', code=279)]
    t = Scripted(auto=True, script=script)
    _, messages = run(t)
    assert messages[-1][0] == 'Failed'
    assert 'iscope_start_stack' not in mutations(t) and 'start_auto_focuse' not in mutations(t)
    assert mutations(t).count('iscope_stop_view') == 1
    if failure == 'AutoFocus': assert 'Sterne' in messages[-1][1]


def test_rejected_stack_is_not_retried():
    t = Scripted(reject='iscope_start_stack')
    with pytest.raises(ValueError): run(t)
    assert mutations(t).count('iscope_start_stack') == 1


def test_failure_received_during_status_read_vetoes_followup():
    class LateFailure(Scripted):
        def send(self, command):
            reply = super().send(command)
            if command['method'] == 'iscope_get_app_state' and self.started and not self.pending:
                for handler in list(self.handlers):
                    handler(event('AutoGoto', 'fail', code=251))
            return reply
    t = LateFailure(); _, messages = run(t)
    assert messages[-1][0] == 'Failed'
    assert 'start_auto_focuse' not in mutations(t)


def test_firmware_flags_are_never_implicitly_changed():
    t = Scripted()
    before = read_state(t); before['stack_after_goto'] = True
    r = Runner(t, 'observe', {}, lambda: None, lambda *args: None)
    with pytest.raises(ValueError): r.run(before)
    assert not mutations(t)


def test_unverified_firmware_stack_is_stopped_without_claiming_success():
    t = Scripted(auto=True, script=SOLVE+[event('Stack', 'working')])
    _, messages = run(t)
    assert messages[-1][0] == 'Unknown'
    assert t.calls[-1][1] == {'method': 'iscope_stop_view', 'params': {'stage': 'Stack'}}


def test_manual_stack_initialisation_failure_stops_own_camera_view():
    class Initialise(Scripted):
        def send(self, command):
            result = super().send(command)
            if command['method'] == 'iscope_start_stack':
                self.started = True
                self.view = {'mode': 'star', 'stage': 'Initialise', 'state': 'working'}
                self.pending = [event('PlateSolve', 'fail', code=251)]
            return result
    t = Initialise(); messages = []
    r = Runner(t, 'stack', {'method': 'iscope_start_stack', 'params': {'restart': False}},
               lambda: None, lambda *args: messages.append(args), interval=.001)
    r.run(read_state(t))
    assert messages[-1][0] == 'Failed'
    assert mutations(t) == ['iscope_start_stack', 'iscope_stop_view']
    assert t.calls[-1][1]['params'] == {'stage': None}


def test_fresh_preflight_detects_capture_started_after_confirmation():
    class NewCapture(Scripted):
        def __init__(self, ip):
            super().__init__(ip, auto=True)
            self.view = {'mode': 'star', 'stage': 'Stack', 'state': 'working'}
    instances = []
    def factory(ip):
        t = NewCapture(ip); instances.append(t); return t
    s = ControlService(factory); s.update_devices(fleet()); s.set_enabled(True)
    try:
        result = s.execute(s.prepare('1', 'observe', {'ra': 1, 'dec': 2})).result(2)
        assert 'bereits aktiv' in result and not mutations(instances[0])
    finally: s.stop()


def test_control_mode_revoked_during_sequence_no_followups():
    enabled = True
    class Revoked(Scripted):
        def send(self, command):
            nonlocal enabled
            result = super().send(command)
            if command['method'] == 'iscope_start_view': enabled = False
            return result
    t = Revoked()
    def guard():
        if not enabled: raise PermissionError()
    r = Runner(t, 'observe', {'method': 'iscope_start_view'}, guard, lambda *a: None)
    with pytest.raises(PermissionError): r.run(read_state(t))
    assert mutations(t) == ['iscope_start_view']


def test_timestamp_from_previous_sequence_is_ignored():
    class OldEvents(Scripted):
        def send(self, command):
            result = super().send(command)
            if command['method'] == 'iscope_start_view': result['Timestamp'] = '100'
            return result
    t = OldEvents(auto=True, script=[{**f, 'Timestamp': '99'} for f in SOLVE + FOCUS + [event('Stack', 'working')]])
    r, messages = run(t)
    assert not r.machine.solved and not r.machine.focused
    assert messages[-1][0] == 'Unknown'


def test_ack_and_mechanical_success_are_not_acquisition_or_stack():
    t = Scripted(script=[event('ScopeGoto', 'complete')])
    r, messages = run(t)
    assert not r.machine.acquired and not r.machine.solved
    assert messages[-1][0] == 'Unknown'
    assert 'start_auto_focuse' not in mutations(t) and 'iscope_start_stack' not in mutations(t)
    assert mutations(t).count('iscope_stop_view') == 1


@pytest.mark.parametrize('phase', ['goto', 'focus', 'stack'])
def test_disconnect_during_each_phase_no_replay(phase):
    t = Scripted(script=['disconnect'] if phase == 'goto' else None,
                 lost={'focus': 'start_auto_focuse', 'stack': 'iscope_start_stack'}.get(phase))
    with pytest.raises(ConnectionError): run(t)
    assert all(mutations(t).count(method) == 1 for method in mutations(t))
    assert not t.handlers


def test_connection_epoch_change_prevents_followups():
    class Reconnected(Scripted):
        def send(self, command):
            result = super().send(command)
            if command['method'] == 'iscope_start_view': self.generation += 1
            return result
    t = Reconnected()
    with pytest.raises(ConnectionError): run(t)
    assert mutations(t) == ['iscope_start_view']


def test_stale_and_inner_success_cannot_finish_sequence():
    m = Observation()
    for f in SOLVE[:-1]: m.event(f)
    m.event(event('AutoGoto', 'complete', page='preview'))
    assert not m.acquired
    m.event(event('AutoFocus', 'complete', page='preview'))
    assert not m.focused


@pytest.mark.parametrize('mode,stage,state,preview,stack', [
    (None, None, None, True, False),
    ('none', 'Stack', 'cancel', True, False),
    ('star', 'ContinuousExposure', 'working', False, True),
    ('star', 'Stack', 'working', False, False),
    ('star', 'AutoFocus', 'working', False, False),
    ('star', 'AutoGoto', 'working', False, False),
    ('star', 'Initialise', 'working', False, False),
    ('scenery', 'RTSP', 'working', False, False),
    ('star', 'ContinuousExposure', 'fail', True, False),
])
def test_preview_stack_gates(mode, stage, state, preview, stack):
    tel = fleet()['1'][1]
    tel = replace(tel, values={**tel.values, 'view_mode': mode, 'view_stage': stage, 'view_state': state})
    assert available('preview', tel) == preview
    assert available('stack', tel) == stack
    assert bool(unavailable_reason('stack', tel.values)) != stack


def test_active_capture_cannot_be_interrupted_or_missing_capability_faked():
    tel = fleet()['1'][1]
    tel = replace(tel, values={**tel.values, 'view_mode': 'star', 'view_stage': 'Stack', 'view_state': 'working'})
    for action in ('goto', 'observe', 'preview', 'autofocus', 'park', 'gain', 'filter'):
        assert not available(action, tel)
    assert available('stop_stack', tel) and available('stop_view', tel)
    assert not available('preview', Telemetry('x', True, values={'parked': False}))


def test_double_click_two_independent_sequences_and_selection_change(app):
    from seestar_studio.control_widget import ControlWidget
    release = threading.Event(); entered = threading.Event(); transports = {}
    class Paused(Scripted):
        def send(self, command):
            if command['method'] == 'iscope_start_view' and self.ip.endswith('.1'):
                entered.set(); release.wait(2)
            return super().send(command)
    def factory(ip):
        t = Paused(ip, auto=True, script=SOLVE + FOCUS + [event('Stack', 'working')])
        transports[ip] = t; return t
    s = ControlService(factory); s.operation_timeout = 8
    w = ControlWidget(s); w.sync_devices(fleet()); w.set_mode(True)
    try:
        w.devices.setCurrentIndex(w.devices.findData('1'))
        f1 = s.execute(s.prepare('1', 'observe', {'ra': 10, 'dec': 20}))
        assert entered.wait(1)
        with pytest.raises(ValueError): s.prepare('1', 'observe', {'ra': 10, 'dec': 20})
        w.devices.setCurrentIndex(w.devices.findData('2'))
        f2 = s.execute(s.prepare('2', 'observe', {'ra': 30, 'dec': 40}))
        release.set()
        # speed up actual Runner intervals for this concurrent integration test
        assert 'Stacking' in f2.result(8)
        assert 'Stacking' in f1.result(8)
        for ip, t in transports.items():
            command = t.calls[0][1]
            assert command['params']['target_ra_dec'][1] == (20 if ip.endswith('.1') else 40)
            assert mutations(t) == ['iscope_start_view']
    finally: release.set(); w.stop(); w.close()


def test_cancel_is_scoped_and_does_not_issue_followup():
    cancel = threading.Event()
    class Cancelled(Scripted):
        def send(self, command):
            r = super().send(command)
            if command['method'] == 'iscope_start_view': cancel.set()
            return r
    t = Cancelled(); _, messages = run(t, cancel=cancel)
    assert messages[-1][0] == 'Cancelled'
    assert mutations(t) == ['iscope_start_view', 'iscope_stop_view']
    assert t.calls[-1][1]['params']['stage'] == 'AutoGoto'


def test_reconnect_reads_actual_state_never_restarts():
    instances = []
    def factory(ip):
        t = Scripted(ip, lost='iscope_start_view' if not instances else None)
        t.auto = True
        if instances: t.view = {'mode': 'star', 'stage': 'Stack', 'state': 'working'}
        instances.append(t); return t
    s = ControlService(factory); s.update_devices(fleet()); s.set_enabled(True)
    try:
        assert 'unklar' in s.execute(s.prepare('1', 'observe', {'ra': 1, 'dec': 2})).result(2)
        s.poll(); s.update_devices(fleet())
        assert 'Stack' in s._jobs['1'].result(2)
        assert len(instances) == 2 and not mutations(instances[1])
        assert s.states['1'] == 'Unknown'
    finally: s.stop()


def test_ui_reasons_languages_readonly_and_preserve_current_filter(app):
    from seestar_studio.control_widget import ControlWidget
    from seestar_studio import i18n
    w = ControlWidget(); w.sync_devices(fleet())
    controller = i18n.TranslationController(app, 'de')
    try:
        w.devices.setCurrentIndex(w.devices.findData('1')); w.refresh()
        assert not w.buttons['preview'].isEnabled() and w.buttons['preview'].toolTip()
        w.set_mode(True); w.refresh()
        assert w.buttons['preview'].isEnabled()  # default: preserve actual filter
        assert not w.buttons['stack'].isEnabled()
        assert 'Sternenvorschau' in w.buttons['stack'].toolTip()
        assert not w.buttons['observe'].isEnabled() and 'Ziel' in w.buttons['observe'].toolTip()
        controller.set_language('en'); w.refresh()
        assert 'GoTo && Start Imaging' in w.buttons['observe'].text()
        assert 'star preview' in w.buttons['stack'].toolTip()
    finally:
        controller.set_language('de'); controller.timer.stop(); app.removeEventFilter(controller)
        controller.deleteLater(); w.stop(); w.close()
