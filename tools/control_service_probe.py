"""Explicit hardware exercise of the production service; no startup/CI use."""
import argparse
import contextlib
from datetime import datetime, timezone
import io
import json
import time
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model', required=True, choices=['Seestar S50', 'Seestar S50 Pro'])
    p.add_argument('--action', required=True, choices=['autofocus', 'observe', 'stop_view', 'park', 'stack'])
    p.add_argument('--execute', action='store_true')
    p.add_argument('--movement-confirmed', action='store_true')
    p.add_argument('--output', required=True)
    args = p.parse_args()
    if not args.execute or not args.movement_confirmed: p.error('Explicit hardware authorization required')
    with contextlib.redirect_stdout(io.StringIO()):
        from telescope_desk.backend import discover
        devices = [d for d in discover() if d.model == args.model]
    if len(devices) != 1: raise RuntimeError('Expected one discovered model')
    from telescope_desk.control import ControlService, create_transport, available
    from telescope_desk.observation import read_state
    from telescope_desk.models import Telemetry
    from tools.control_hardware_probe import clean
    info = devices[0]
    report = dict(model=info.model, action=args.action, utc=datetime.now(timezone.utc).isoformat(),
                  commands=[], events=[], production_service=True, movement_space_confirmed=True)
    def factory(ip):
        t = create_transport(ip)
        original = t.send
        def send(command):
            reply = original(command)
            if command['method'] not in ('test_connection', 'get_device_state', 'iscope_get_app_state', 'get_wheel_position'):
                report['commands'].append(dict(command=command, response=clean(reply)))
            return reply
        t.send = send
        t.add_event_handler(lambda f: report['events'].append(clean(f)) if f.get('Event') in
                            ('AutoGoto','ScopeGoto','PlateSolve','AutoFocus','Stack','View','ScopeHome') else None)
        return t
    reader = create_transport(info.ip); service = ControlService(factory)
    service.operation_timeout = 80
    def refresh():
        state = read_state(reader)
        tel = Telemetry(info.serial, True, values={**state, 'age_s': 0})
        service.update_devices({info.serial: (info, tel, None)})
        return state, tel
    try:
        reader.connect()
        if not reader.matches_serial(info.serial): raise RuntimeError('Identity mismatch')
        before, tel = refresh(); report['before'] = before
        report['availability_before'] = {a: available(a, tel) for a in ('preview','stack','autofocus','observe','park')}
        params = {}
        if args.action == 'observe':
            from telescope_desk.sky.catalog import Catalog
            from astropy.coordinates import SkyCoord, get_sun
            from astropy.time import Time
            from astropy import units as u
            target = Catalog().search('M81')[0]
            sun = get_sun(Time.now())
            separation = SkyCoord(target.ra*u.deg,target.dec*u.deg).separation(SkyCoord(sun.ra,sun.dec)).deg
            if separation < 45: raise RuntimeError('Too close to Sun')
            report['sun_separation_deg'] = float(separation)
            params = dict(ra=target.ra, dec=target.dec, target=target.id)
        service.set_enabled(True)
        future = service.execute(service.prepare(info.serial, args.action, params))
        while not future.done():
            refresh(); time.sleep(1)
        service.poll()
        report['result'] = future.result()
        report['state'] = service.states.get(info.serial)
        report['history'] = service.histories.get(info.serial)
        report['after'], tel = refresh()
        report['availability_after'] = {a: available(a, tel) for a in ('preview','stack','autofocus','observe','park')}
    except Exception as exc:
        service.set_enabled(False)
        report['error'] = type(exc).__name__
    finally:
        service.stop(); reader.close()
        while service.running: time.sleep(.1)
        Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
        print(json.dumps({k:v for k,v in report.items() if k not in ('events','before','after')},ensure_ascii=False,indent=2))


if __name__ == '__main__': main()
