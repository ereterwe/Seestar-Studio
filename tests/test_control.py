from dataclasses import replace
import threading
import time
import pytest
from telescope_desk.control import ControlService, payload, available
from telescope_desk.models import DeviceInfo, Telemetry


def fleet():
    return {sn: (DeviceInfo(sn, '127.0.0.' + sn), Telemetry(sn, True, values={
        'age_s': 1, 'ra': 2, 'dec': 30, 'parked': False, 'equ_mode': True,
        'tracking': True, 'view_mode': 'none', 'view_stage': None, 'view_state': 'cancel', 'target': 'TEST',
        'move_type': 'none', 'camera_ready': True, 'auto_af': True, 'stack_after_goto': True,
        'exp_s': 10, 'gain': 80, 'filter': 'LP', 'has_focuser': True}), None) for sn in ('1', '2')}


class FakeTransport:
    calls = []
    def __init__(self, ip): self.ip = ip; self.handlers = []; self.generation = 1
    def connect(self): pass
    def matches_serial(self, serial): return self.ip.endswith('.' + serial)
    def close(self): pass
    def add_event_handler(self, handler): self.handlers.append(handler)
    def remove_event_handler(self, handler): self.handlers.remove(handler)
    def send(self, command):
        if command['method'] == 'iscope_get_app_state': return {'code': 0, 'result': {}}
        if command['method'] == 'get_device_state': return {'code': 0, 'result': {
            'mount': {'close': False, 'equ_mode': True, 'move_type': 'none', 'tracking': True},
            'camera': {'name': 'simulated'}, 'focuser': {'state': 'idle'},
            'setting': {'auto_af': True, 'stack_after_goto': True}}}
        if command['method'] == 'get_wheel_position': return {'code': 0, 'result': 1}
        if command['method'] == 'test_connection': return {'code': 0}
        self.calls.append((self.ip, command))
        event = {'scope_goto': 'ScopeGoto', 'scope_park': 'ScopeHome'}.get(command['method'])
        if event:
            for handler in list(self.handlers): handler({'Event': event, 'state': 'complete', 'lapse_ms': 20})
        return {'code': 0, 'result': 'ok'}


def test_read_only_confirm_once_target_and_revoke():
    FakeTransport.calls = []
    s = ControlService(FakeTransport)
    s.update_devices(fleet())
    try:
        with pytest.raises(PermissionError): s.prepare('1', 'park', {})
        s.set_enabled(True)
        intent = s.prepare('2', 'goto', {'ra': 180, 'dec': 40})
        assert 'abgeschlossen' in s.execute(intent).result(2)
        assert FakeTransport.calls == [('127.0.0.2', {'method': 'scope_goto', 'params': [12.0, 40.0]})]
        with pytest.raises(PermissionError): s.execute(intent)
        intent = s.prepare('1', 'park', {})
        s.set_enabled(False)
        with pytest.raises(PermissionError): s.execute(intent)
    finally: s.stop()


@pytest.mark.parametrize('change', ['ip', 'target', 'offline', 'expired'])
def test_stale_confirmation_never_sends(change):
    s = ControlService(lambda ip: pytest.fail('Must not create transport'))
    data = fleet(); s.update_devices(data); s.set_enabled(True)
    intent = s.prepare('1', 'park', {})
    info, tel, frame = data['1']
    if change == 'ip': info = replace(info, ip='127.0.0.9')
    if change == 'target': tel = replace(tel, values={**tel.values, 'target': 'DIFFERENT'})
    if change == 'offline': tel = replace(tel, connected=False)
    if change == 'expired': intent = replace(intent, expires=0)
    data['1'] = info, tel, frame; s.update_devices(data)
    with pytest.raises((PermissionError, ValueError)): s.execute(intent)
    s.stop()


def test_lost_reply_is_not_retried_and_other_device_works():
    class Lost(FakeTransport):
        calls = []
        def send(self, command):
            if command['method'] == 'scope_park' and self.ip.endswith('.1'):
                self.calls.append((self.ip, command)); raise TimeoutError()
            return super().send(command)
    s = ControlService(Lost); s.update_devices(fleet()); s.set_enabled(True)
    try:
        f1 = s.execute(s.prepare('1', 'park', {}))
        f2 = s.execute(s.prepare('2', 'tracking_on', {}))
        assert 'unklar' in f1.result(2)
        assert 'angenommen' in f2.result(2)
        assert sorted(ip for ip, _ in Lost.calls) == ['127.0.0.1', '127.0.0.2']
    finally: s.stop()


def test_mode_revoked_during_auth_prevents_mutation():
    started, resume = threading.Event(), threading.Event()
    class Slow(FakeTransport):
        def connect(self): started.set(); resume.wait(2)
        def send(self, command): pytest.fail('Mutation after revocation')
    s = ControlService(Slow); s.update_devices(fleet()); s.set_enabled(True)
    try:
        f = s.execute(s.prepare('1', 'park', {}))
        assert started.wait(1)
        s.set_enabled(False); resume.set()
        assert 'Nicht gesendet' in f.result(2)
    finally: resume.set(); s.stop()


def test_payload_bounds_preserve_mount_and_no_implicit_restart():
    tel = fleet()['1'][1]
    assert payload('park', {}, tel)['params'] == {'equ_mode': True}
    assert payload('stack', {}, tel)['params'] == {'restart': False}
    assert payload('exposure', {'seconds': 30}, tel)['params']['exp_ms']['stack_l'] == 30000
    for action, parameters in [('goto', {'ra': float('nan'), 'dec': 0}), ('gain', {'gain': -1}),
                               ('filter', {'position': 5}), ('exposure', {'seconds': 13}), ('reboot', {})]:
        with pytest.raises(ValueError): payload(action, parameters, tel)
    assert not available('park', Telemetry('x', True))


def test_control_ui_starts_locked_and_selection_is_explicit(app):
    from telescope_desk.control_widget import ControlWidget
    widget = ControlWidget(ControlService(lambda ip: pytest.fail('No UI action authorized')))
    widget.sync_devices(fleet())
    assert widget.devices.currentData() is None
    assert not widget.service.enabled
    assert not any(b.isEnabled() for b in widget.buttons.values())
    widget.stop(); widget.close()


def test_actual_transport_does_not_replay_on_lost_response(monkeypatch):
    import socket
    import json
    from seestarpy import auth
    from telescope_desk.control import create_transport
    sent = []
    class Socket:
        def settimeout(self, value): pass
        def connect(self, address): pass
        def close(self): pass
        def sendall(self, data): sent.append(json.loads(data))
        def recv(self, size): raise TimeoutError('simulated lost reply')
    monkeypatch.setattr(socket, 'socket', lambda *args: Socket())
    monkeypatch.setattr(auth, 'KEY_PATH', None)
    transport = create_transport('127.0.0.1')
    try:
        transport.connect()
        with pytest.raises(TimeoutError): transport.send({'method': 'scope_park', 'params': {'equ_mode': True}})
        assert len(sent) == 1 and sent[0]['method'] == 'scope_park'
        with pytest.raises(PermissionError): transport.send({'method': 'pi_reboot'})
        assert len(sent) == 1
    finally: transport.close()


def test_dhcp_reassignment_never_receives_mutation():
    class WrongDevice(FakeTransport):
        def matches_serial(self, serial): return False
        def send(self, command): pytest.fail('Wrong telescope received a command')
    s = ControlService(WrongDevice); s.update_devices(fleet()); s.set_enabled(True)
    try:
        result = s.execute(s.prepare('1', 'park', {})).result(2)
        assert 'Geräteidentität' in result and 'Nicht gesendet' in result
    finally: s.stop()
