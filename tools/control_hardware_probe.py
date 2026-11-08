"""Manually invoked, bounded indoor control diagnosis; NEVER startup/CI code.

Requires a separate operator movement confirmation and explicit action. Starts
one discovered model only. No raw auth/state dumping or persistent settings.
"""
import argparse
import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import time

EVENTS = {'View','ScopeGoto','AutoGoto','AutoGotoStep','PlateSolve','AutoFocus',
          'Stack','ContinuousExposure','ScopeHome','ScopeMoveToHorizon','ScopeTrack','Alert'}
FIELDS = {'Event','state','stage','mode','code','error','lapse_ms','route','page','count',
          'stacked_frame','dropped_frame','cam_id','Timestamp'}


def clean(data):
    if not isinstance(data,dict): return {}
    return {k:clean(v) if isinstance(v,dict) else v for k,v in data.items() if k in EVENTS or k in FIELDS}


def read_state(transport):
    app=transport.send({'method':'iscope_get_app_state'})
    device=transport.send({'method':'get_device_state','params':{'keys':['device','mount','focuser','camera','setting']}})
    if app.get('code')!=0 or device.get('code')!=0:raise RuntimeError('Status read rejected')
    result=device.get('result') or {}
    return {'app':clean(app.get('result') or {}),
            'mount':result.get('mount',{}),'focuser':result.get('focuser',{}),
            'setting':{k:(result.get('setting') or {}).get(k) for k in ('auto_af','stack_after_goto')},
            'camera_available':bool(result.get('camera'))}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--model',required=True,choices=['Seestar S50','Seestar S50 Pro'])
    parser.add_argument('--action',default='read',choices=['read','unpark','preview','autofocus','goto','observe','stack','stop_stack','stop_view','park'])
    parser.add_argument('--execute',action='store_true')
    parser.add_argument('--movement-confirmed',action='store_true')
    parser.add_argument('--target',default='M81')
    parser.add_argument('--seconds',type=int,default=45)
    parser.add_argument('--output',required=True)
    args=parser.parse_args()
    if args.action!='read' and not (args.execute and args.movement_confirmed):
        parser.error('Explicit execution and operator-confirmed free movement space required')
    if not 5<=args.seconds<=300:parser.error('Bounded duration required')
    with contextlib.redirect_stdout(io.StringIO()):
        from telescope_desk.backend import discover
        from telescope_desk.control import create_transport
        devices=[d for d in discover() if d.model==args.model]
    if len(devices)!=1:raise RuntimeError('Expected one freshly discovered matching model')
    info=devices[0];transport=create_transport(info.ip)
    report={'model':info.model,'action':args.action,'utc':datetime.now(timezone.utc).isoformat(),
            'movement_space_confirmed':args.movement_confirmed,'events':[],'commands':[]}
    seen=[]
    def event(frame):
        if frame.get('Event') in EVENTS:
            data=clean(frame);data['received_utc']=datetime.now(timezone.utc).isoformat()
            report['events'].append(data);seen.append(frame)
    transport.connection.add_event_handler(event)
    terminal=None;started=False
    try:
        transport.connect()
        if not transport.matches_serial(info.serial):raise RuntimeError('Device identity mismatch')
        before=read_state(transport);report['before']=before
        view=before['app'].get('View') or {}
        busy=view.get('state') in ('working','start')
        stacking=view.get('stage')=='Stack' and busy
        if args.action in ('goto','observe','unpark','park','preview') and busy:
            raise RuntimeError('Existing view/operation active; not interrupted')
        if args.action in ('autofocus','stack') and (view.get('mode')!='star' or view.get('stage')!='ContinuousExposure' or not busy):
            raise RuntimeError('Confirmed active astronomical preview required')
        if args.action=='stop_stack' and not stacking:raise RuntimeError('No active stack to stop')
        if args.action in ('autofocus','stack') and stacking:raise RuntimeError('Existing stacking not interrupted')
        command=None
        if args.action=='unpark':command={'method':'scope_move_to_horizon'};terminal='ScopeMoveToHorizon'
        elif args.action=='park':
            mode=before['mount'].get('equ_mode')
            if type(mode) is not bool:raise RuntimeError('Mount mode unknown')
            command={'method':'scope_park','params':{'equ_mode':mode}};terminal='ScopeHome'
        elif args.action in ('preview','observe','goto'):
            if before['mount'].get('close') is not False:raise RuntimeError('Unpark explicitly first')
            params={'mode':'star','target_ra_dec':[None,None],'target_name':'Studio Indoor Test'}
            if args.action in ('observe','goto'):
                from telescope_desk.sky.catalog import Catalog
                from astropy.coordinates import SkyCoord,get_sun
                from astropy.time import Time
                from astropy import units as u
                matches=Catalog().search(args.target)
                if not matches or not matches[0].valid:raise RuntimeError('Invalid local catalogue target')
                target=matches[0]
                # Use geocentric apparent solar direction, not barycentric Sun origin.
                sun=get_sun(Time.now())
                separation=SkyCoord(target.ra*u.deg,target.dec*u.deg).separation(SkyCoord(sun.ra,sun.dec)).deg
                if separation<45:raise RuntimeError('Target too close to Sun for test')
                params.update(target_ra_dec=[target.ra/15,target.dec],target_name=target.id)
                report['sun_separation_deg']=float(separation)
            if args.action=='goto':
                command={'method':'scope_goto','params':params['target_ra_dec']};terminal='ScopeGoto'
            else:
                wheel=transport.send({'method':'get_wheel_position'})
                value=wheel.get('result')
                if isinstance(value,dict):value=value.get('position')
                if wheel.get('code')!=0 or value not in (1,2):raise RuntimeError('Current imaging filter unknown; not changed')
                params['lp_filter']=value==2
                command={'method':'iscope_start_view','params':params}
                terminal='AutoGoto' if args.action=='observe' else 'ContinuousExposure'
        elif args.action=='autofocus':command={'method':'start_auto_focuse'};terminal='AutoFocus'
        elif args.action=='stack':command={'method':'iscope_start_stack','params':{'restart':False}};terminal='Stack'
        elif args.action in ('stop_stack','stop_view'):
            command={'method':'iscope_stop_view','params':{'stage':'Stack' if args.action=='stop_stack' else None}}
        if command:
            reply=transport.send(command);started=True
            report['commands'].append({'command':command,'response':clean(reply),'accepted':reply.get('code')==0 and not reply.get('error')})
            print(args.model,args.action,'reply code',reply.get('code'),flush=True)
            if reply.get('code')!=0:report['outcome']='Command rejected';return
        deadline=time.monotonic()+args.seconds
        while time.monotonic()<deadline:
            transport.send({'method':'test_connection'})
            if args.action=='observe' and any(f.get('Event')=='PlateSolve' and f.get('state')=='fail' for f in seen):
                reply=transport.send({'method':'iscope_stop_view','params':{'stage':'AutoGoto'}})
                report['commands'].append({'command':{'method':'iscope_stop_view','params':{'stage':'AutoGoto'}},'response':clean(reply),'reason':'Stop own test after first plate-solving failure'})
                report['outcome']='Operation failed: PlateSolve; not verifiable indoors'
                break
            outer=[f for f in seen if f.get('Event')==terminal and f.get('state') in ('complete','fail','cancel') and 'page' not in f]
            active=[f for f in seen if f.get('Event')==terminal and f.get('state') in ('working','start')]
            if outer:
                report['outcome']='Operation '+outer[-1]['state'];break
            if args.action in ('preview','stack') and active:
                report['outcome']='Operation started';break
            if args.action in ('read','stop_stack','stop_view'):break
            time.sleep(.5)
        else:
            report['outcome']='Timeout; not completed'
            if started and terminal in ('AutoGoto','AutoFocus'):
                reply=transport.send({'method':'iscope_stop_view','params':{'stage':terminal}})
                report['commands'].append({'command':{'method':'iscope_stop_view','params':{'stage':terminal}},'response':clean(reply),'reason':'bounded stop of own test operation'})
        report['after']=read_state(transport)
    except Exception as exc:
        report['probe_error']=type(exc).__name__+': '+str(exc)[:160]
    finally:
        transport.close()
        path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':main()
