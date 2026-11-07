"""Explicit, one-shot control intents; independent of read-only viewer sockets."""
from .i18n import source as ui_text, tr
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import json
import math
import threading
import time
import uuid
from .observation import Runner, LABELS, ACTIVE, read_state
ACTIONS = {'observe': ui_text('ctl_observe'), 'goto': ui_text('ctl_goto_only'), 'unpark': ui_text('ctl_unpark'), 'tracking_on': ui_text('m0028'), 'tracking_off': ui_text('m0029'), 'preview': ui_text('m0030'), 'stack': ui_text('m0031'), 'stop_stack': ui_text('m0032'), 'stop_view': ui_text('m0033'), 'exposure': ui_text('m0034'), 'gain': ui_text('m0035'), 'filter': ui_text('m0036'), 'autofocus': ui_text('m0037'), 'park': ui_text('m0038')}
CONTROL_READ_METHODS = frozenset({'test_connection', 'get_device_state', 'get_setting', 'get_view_state', 'iscope_get_app_state', 'get_wheel_position'})
CONTROL_METHODS = CONTROL_READ_METHODS | frozenset({'scope_goto', 'scope_set_track_state', 'iscope_start_view', 'iscope_start_stack', 'iscope_stop_view', 'set_setting', 'set_control_value', 'set_wheel_position', 'start_auto_focuse', 'scope_park', 'scope_move_to_horizon'})

def unavailable_reason(action, v):
    """Capability and activity evidence, shared by UI and fresh wire preflight."""
    if action not in ACTIONS: return ui_text('m0057')
    active = v.get('view_state') in ACTIVE
    stage = v.get('view_stage')
    moving = v.get('move_type') not in (None, 'none')
    if action == 'stop_view':
        return '' if active else ui_text('ctl_no_view')
    if action == 'stop_stack':
        return '' if active and stage == 'Stack' else ui_text('ctl_no_stack')
    if moving: return ui_text('ctl_slewing')
    if active and stage in ('AutoGoto', 'ScopeGoto', 'PlateSolve', 'AutoFocus', 'Initialise'):
        return ui_text('ctl_operation_busy')
    if active and stage == 'Stack': return ui_text('ctl_already_stack')
    if action in ('goto', 'observe', 'preview', 'park', 'unpark') and active:
        return ui_text('ctl_existing_view')
    if action == 'unpark':
        return '' if v.get('parked') is True else ui_text('ctl_not_parked')
    if action == 'park':
        return '' if type(v.get('equ_mode')) is bool and v.get('parked') is False else ui_text('ctl_mount_unknown')
    if v.get('parked') is not False: return ui_text('ctl_parked')
    if action in ('preview', 'observe') and v.get('camera_ready') is not True:
        return ui_text('ctl_camera_unknown')
    if action == 'observe':
        if v.get('has_focuser') is not True: return ui_text('ctl_focuser_unknown')
        if any(type(v.get(k)) is not bool for k in ('auto_af', 'stack_after_goto')):
            return ui_text('ctl_flags_unknown')
        if v['stack_after_goto'] and not v['auto_af']: return ui_text('ctl_flags_conflict')
    if action in ('stack', 'autofocus'):
        if not (active and stage == 'ContinuousExposure' and v.get('view_mode') == 'star'):
            return ui_text('ctl_no_preview')
        if action == 'autofocus' and v.get('has_focuser') is not True:
            return ui_text('ctl_focuser_unknown')
    if action.startswith('tracking_') and type(v.get('tracking')) is not bool:
        return ui_text('ctl_mount_unknown')
    if action in ('exposure', 'gain', 'filter'):
        key = {'exposure': 'exp_s', 'gain': 'gain', 'filter': 'filter'}[action]
        if v.get(key) is None: return ui_text('m0057')
    return ''

def available(action, telemetry):
    return not unavailable_reason(action, telemetry.values)

def payload(action, parameters, telemetry):
    p = dict(parameters)
    if action in ('goto', 'observe'):
        ra, dec = (float(p['ra']), float(p['dec']))
        if not math.isfinite(ra) or not math.isfinite(dec) or (not 0 <= ra < 360) or (not -90 <= dec <= 90):
            raise ValueError(ui_text('m0043'))
        if action == 'goto': return {'method': 'scope_goto', 'params': [ra / 15, dec]}
        return {'method': 'iscope_start_view', 'params': {'mode': 'star', 'target_ra_dec': [ra / 15, dec], 'target_name': str(p.get('target', 'Studio Target'))[:160]}}
    if action == 'unpark': return {'method': 'scope_move_to_horizon'}
    if action.startswith('tracking_') and action in ACTIONS:
        return {'method': 'scope_set_track_state', 'params': action == 'tracking_on'}
    if action == 'preview':
        if p.get('filter') not in (None, 1, 2):
            raise ValueError(ui_text('m0044'))
        result = {'method': 'iscope_start_view', 'params': {'mode': 'star', 'target_ra_dec': [None, None], 'target_name': 'Studio Preview'}}
        if p.get('filter') is not None: result['params']['lp_filter'] = p['filter'] == 2
        return result
    if action == 'stack':
        return {'method': 'iscope_start_stack', 'params': {'restart': False}}
    if action in ('stop_stack', 'stop_view'):
        return {'method': 'iscope_stop_view', 'params': {'stage': 'Stack' if action == 'stop_stack' else None}}
    if action == 'exposure':
        value = p.get('seconds')
        if type(value) is not int or value not in (2, 5, 10, 20, 30, 60):
            raise ValueError(ui_text('m0045'))
        return {'method': 'set_setting', 'params': {'expert_mode': True, 'exp_ms': {'stack_l': value * 1000}}}
    if action == 'gain':
        value = p.get('gain')
        if type(value) is not int or not 0 <= value <= 1000:
            raise ValueError(ui_text('m0046'))
        return {'method': 'set_control_value', 'params': ['gain', value]}
    if action == 'filter':
        if type(p.get('position')) is not int or p['position'] not in (0, 1, 2):
            raise ValueError(ui_text('m0047'))
        return {'method': 'set_wheel_position', 'params': [p['position']]}
    if action == 'autofocus':
        return {'method': 'start_auto_focuse'}
    if action == 'park':
        equ_mode = telemetry.get('equ_mode')
        if type(equ_mode) is not bool:
            raise ValueError(ui_text('m0048'))
        return {'method': 'scope_park', 'params': {'equ_mode': equ_mode}}
    raise ValueError(ui_text('m0039'))

def fingerprint(info, telemetry):
    return (info.serial, info.ip, *(telemetry.get(k) for k in ('target', 'view_mode', 'view_stage', 'view_state', 'equ_mode', 'parked', 'filter', 'exp_s', 'gain', 'auto_af', 'stack_after_goto', 'move_type')))

@dataclass(frozen=True)
class Intent:
    token: str
    serial: str
    action: str
    command_json: str
    fingerprint: tuple
    expires: float
    description: str

class ControlService:

    def __init__(self, factory=None):
        self.factory = factory or create_transport
        self.enabled = False
        self.devices = {}
        self._lock = threading.RLock()
        self._intents = {}
        self._pools, self._transports, self._jobs = ({}, {}, {})
        self.results = {}
        self.states, self.histories, self._cancels = {}, {}, {}
        self.operation_timeout = 300
        self._recovery_pending = set()
        self._stopped = False

    def set_enabled(self, enabled):
        with self._lock:
            self.enabled = bool(enabled) and (not self._stopped)
            self._intents.clear()

    def update_devices(self, data):
        with self._lock:
            self.devices = dict(data)
            for serial in tuple(self._recovery_pending):
                record = data.get(serial)
                if self._stopped or not record or not record[1].connected or self.busy(serial): continue
                self._recovery_pending.discard(serial)
                self._jobs[serial] = self._pools[serial].submit(self._readback, record[0])

    def _readback(self, info):
        """One read-only recovery, never resume an interrupted sequence."""
        transport = self.factory(info.ip)
        try:
            transport.connect()
            if not transport.matches_serial(info.serial): return ui_text('m0052')
            generation = getattr(transport, 'generation', 0)
            state = read_state(transport)
            if getattr(transport, 'generation', 0) != generation: raise ConnectionError()
            return ui_text('ctl_reconnected').format(p0=state['view_mode'] or '—',
                                                    p1=state['view_stage'] or '—',
                                                    p2=state['view_state'] or '—')
        except Exception:
            return ui_text('ctl_connection_unknown')
        finally: transport.close()

    def _check(self, serial):
        if not self.enabled or self._stopped:
            raise PermissionError(ui_text('m0049'))
        if serial not in self.devices:
            raise ValueError(ui_text('m0050'))
        info, tel, _ = self.devices[serial]
        if not tel.connected or tel.paused or tel.get('age_s') is None or (tel.get('age_s') > 20) or (time.time() - tel.observed_at > 20):
            raise ValueError(ui_text('m0051'))
        return (info, tel)

    def prepare(self, serial, action, parameters):
        with self._lock:
            info, tel = self._check(serial)
            if not available(action, tel):
                raise ValueError(unavailable_reason(action, tel.values))
            if serial in self._jobs and (not self._jobs[serial].done()):
                raise ValueError(ui_text('m0058'))
            command = payload(action, parameters, tel)
            details = json.dumps(parameters, ensure_ascii=False)
            description = ui_text('m0040').format(p0=f'{ACTIONS[action]}', p1=f'{info.model}', p2=f'{info.serial}', p3=f"{tel.get('target') or '—'}", p4=f"{tel.get('view_stage') or '—'}", p5=f'{details}')
            if action in ('observe', 'goto', 'park', 'unpark', 'autofocus'):
                description += '\n\n' + ui_text('ctl_confirm_space')
            if action == 'observe': description += '\n' + ui_text('ctl_confirm_sequence')
            token = uuid.uuid4().hex
            intent = Intent(token, serial, action, json.dumps(command), fingerprint(info, tel), time.monotonic() + 30, description)
            self._intents = {k: v for k, v in self._intents.items() if v.serial != serial and v.expires > time.monotonic()}
            self._intents[token] = intent
            return intent

    def execute(self, intent):
        with self._lock:
            stored = self._intents.pop(intent.token, None)
            if stored != intent or time.monotonic() > intent.expires:
                raise PermissionError(ui_text('m0059'))
            info, tel = self._check(intent.serial)
            if fingerprint(info, tel) != intent.fingerprint:
                raise PermissionError(ui_text('m0060'))
            if intent.serial in self._jobs and (not self._jobs[intent.serial].done()):
                raise PermissionError(ui_text('m0061'))
            if intent.serial not in self._pools:
                self._pools[intent.serial] = ThreadPoolExecutor(max_workers=1, thread_name_prefix='studio-control')
            pool = self._pools[intent.serial]
            self._cancels[intent.serial] = threading.Event()
            self.states[intent.serial] = 'TargetSelected' if intent.action in ('goto', 'observe') else 'Idle'
            self.histories[intent.serial] = []
            future = pool.submit(self._send, intent, info)
            self._jobs[intent.serial] = future
            self.results[intent.serial] = ui_text('m0041')
            return future

    def _send(self, intent, info):
        try:
            with self._lock:
                current, tel = self._check(intent.serial)
                if fingerprint(current, tel) != intent.fingerprint or time.monotonic() > intent.expires:
                    return ui_text('m0062')
            transport = self._transports.get(intent.serial)
            if transport and transport.ip != info.ip:
                transport.close()
                transport = None
            if transport is None:
                transport = self.factory(info.ip)
                self._transports[intent.serial] = transport
            transport.connect()
            if not transport.matches_serial(intent.serial):
                return ui_text('m0052')
            with self._lock:
                current, tel = self._check(intent.serial)
                if fingerprint(current, tel) != intent.fingerprint or time.monotonic() > intent.expires:
                    return ui_text('m0062')
            generation = getattr(transport, 'generation', 0)
            def guard():
                with self._lock:
                    try: current, _ = self._check(intent.serial)
                    except ValueError as exc: raise ConnectionError('Current device status unavailable') from exc
                    if current.ip != info.ip or getattr(transport, 'generation', 0) != generation:
                        raise ConnectionError('Device connection changed')
            guard()
            before = read_state(transport)
            guard()
            reason = unavailable_reason(intent.action, {**tel.values, **before})
            if reason: return reason
            # Mount mode is persistent: never send a stale value back on park.
            if intent.action == 'park' and before['equ_mode'] != tel.get('equ_mode'):
                return ui_text('m0062')
            if intent.action == 'observe' and any(before[k] != tel.get(k) for k in ('auto_af', 'stack_after_goto')):
                return ui_text('m0062')
            command = json.loads(intent.command_json)
            if intent.action in ('preview', 'observe') and 'lp_filter' not in command['params']:
                wheel = transport.send({'method': 'get_wheel_position'})
                position = wheel.get('result')
                if isinstance(position, dict): position = position.get('position')
                if wheel.get('code') != 0 or position not in (1, 2): return ui_text('ctl_filter_unknown')
                command['params']['lp_filter'] = position == 2
            def publish(state, detail=''):
                with self._lock:
                    self.states[intent.serial] = state
                    message = LABELS[state] + ((' · ' + detail) if detail else '')
                    self.results[intent.serial] = message
                    history = self.histories.setdefault(intent.serial, [])
                    if not history or history[-1] != message: history.append(message)
                    del history[:-32]
            runner = Runner(transport, intent.action, command, guard, publish,
                            self._cancels[intent.serial], timeout=self.operation_timeout)
            runner.run(before)
            return self.results.get(intent.serial, ui_text('ctl_accepted'))
        except PermissionError:
            self.states[intent.serial] = 'Unknown'
            return ui_text('ctl_revoked')
        except ValueError as exc:
            self.states[intent.serial] = 'Failed'
            return ui_text('ctl_failed') + ' · ' + str(exc)
        except Exception:
            # Do not replay a mutation after a lost response. A NEW identified
            # read-only connection may report what the device actually does.
            self.states[intent.serial] = 'Unknown'
            self._recovery_pending.add(intent.serial)
            transport = self._transports.pop(intent.serial, None)
            if transport: transport.close()
            return ui_text('ctl_connection_unknown')

    def cancel(self, serial):
        with self._lock:
            self._check(serial)
            if serial in self._cancels: self._cancels[serial].set()

    def busy(self, serial):
        with self._lock:
            return serial in self._jobs and not self._jobs[serial].done()

    def poll(self):
        with self._lock:
            for serial, future in list(self._jobs.items()):
                if future.done():
                    try:
                        self.results[serial] = future.result()
                    except Exception:
                        self.results[serial] = ui_text('m0063')
                    del self._jobs[serial]

    @property
    def running(self):
        return any((not future.done() for future in self._jobs.values()))

    def stop(self):
        self.set_enabled(False)
        self._stopped = True
        for serial, pool in self._pools.items():

            def close_transport(sn=serial):
                transport = self._transports.pop(sn, None)
                if transport:
                    transport.close()
                return ui_text('m0056')
            self._jobs[serial] = pool.submit(close_transport)
            pool.shutdown(wait=False)

def create_transport(ip):
    """Lazy import: no discovery or authentication on GUI construction."""
    import socket
    from seestarpy import connection, auth

    class BoundedSocket:

        def __init__(self, sock):
            self.sock = sock
            self.reset()

        def reset(self):
            self.deadline, self.remaining = (time.monotonic() + 30, 2 * 1024 * 1024)

        def __getattr__(self, name):
            return getattr(self.sock, name)

        def recv(self, size):
            if time.monotonic() > self.deadline or self.remaining <= 0:
                raise TimeoutError('Bounded RPC receive expired')
            data = self.sock.recv(min(size, self.remaining))
            self.remaining -= len(data)
            return data

    class SingleAttemptConnection(connection._Connection):

        generation = 0

        def _connect(self):
            sock = BoundedSocket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            try:
                sock.settimeout(5)
                sock.connect((self.ip, self.port))
                if auth.KEY_PATH is not None:
                    auth.authenticate(sock)
                self._sock, self._buf = (sock, '')
                self.generation += 1
            except Exception:
                sock.close()
                raise

        def send(self, params, quiet=True):
            if params.get('method') not in CONTROL_METHODS:
                raise PermissionError('Unaudited control method')
            with self._lock:
                if self._sock is None:
                    if params.get('method') not in {'test_connection', 'get_device_state'}:
                        raise ConnectionError('Control socket changed after identity check')
                    self._connect()
                self._sock.reset()
                ident = uuid.uuid4().int % 2 ** 31
                try:
                    return self._send_once({'id': ident, 'verify': True, **params}, ident, quiet=True)
                except Exception:
                    self._close_locked()
                    raise

    class Transport:

        def __init__(self):
            self.ip = ip
            self.connection = SingleAttemptConnection(ip)
            self.keepalive = False

        @property
        def generation(self): return self.connection.generation

        def add_event_handler(self, handler): self.connection.add_event_handler(handler)

        def remove_event_handler(self, handler): self.connection.remove_event_handler(handler)

        def connect(self):
            with self.connection._lock:
                if self.connection._sock is None:
                    self.connection._connect()

        def send(self, command):
            if not self.keepalive:
                self.connection.start_keepalive()
                self.keepalive = True
            return self.connection.send(command)

        def matches_serial(self, serial):
            response = self.connection.send({'method': 'get_device_state', 'params': {'keys': ['device']}})
            device = (response.get('result') or {}).get('device') or {}
            return response.get('code') == 0 and str(device.get('sn', '')).casefold() == serial.casefold()

        def close(self):
            self.connection.stop_keepalive(force=True)
            self.connection.close()
    return Transport()
