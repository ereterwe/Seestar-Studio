from types import SimpleNamespace as NS
import pytest
from telescope_desk.location import LocationProposal, WindowsLocationRequest, windows_proposal
from telescope_desk.sky.site import SiteDialog


def position(accuracy=20, reference=3, altitude_accuracy=5):
    return NS(coordinate=NS(accuracy=accuracy, altitude_accuracy=altitude_accuracy,
        point=NS(altitude_reference_system=reference, position=NS(latitude=52.,longitude=13.,altitude=45.))))


def test_windows_accuracy_and_height_reference():
    assert windows_proposal(position()).elevation == 45
    assert windows_proposal(position(reference=2)).elevation is None
    assert windows_proposal(position(altitude_accuracy=None)).elevation is None
    assert windows_proposal(position(altitude_accuracy=500)).elevation is None
    assert windows_proposal(position(accuracy=8000)).accuracy == 8000
    for lat,lon in [(float('nan'),0),(91,0),(0,181),(True,0)]:
        with pytest.raises(ValueError): LocationProposal(lat,lon)


class Operation:
    def __init__(self,result=None,status=1):self.result=result;self.status=status;self.cancelled=False
    def get_results(self):
        if self.status==3:raise OSError('private unlogged detail')
        return self.result
    def cancel(self):self.cancelled=True
    def close(self):pass


def api(permission=1, available=True):
    class API:
        requested=0
        @classmethod
        def request_access_async(cls):
            cls.requested+=1
            if not available:raise OSError()
            return Operation(permission)
        def get_geoposition_async_with_age_and_timeout(self,age,timeout):return Operation(position())
    return API


def test_windows_request_denied_missing_success_and_cancellation(app):
    for permission,available,expected in [(2,True,False),(1,False,False),(1,True,True)]:
        backend=api(permission,available);request=WindowsLocationRequest(api=backend)
        proposals=[];errors=[];request.proposal.connect(proposals.append);request.failed.connect(errors.append)
        assert backend.requested==0
        request.start();request.poll();request.poll()
        assert bool(proposals)==expected and bool(errors)!=expected
        assert request.operation is None and not request.timer.isActive()
        request.deleteLater()
    request=WindowsLocationRequest(api=api());op=Operation(status=0);request.operation=op
    request.cancel();assert op.cancelled
    request.deleteLater()


def test_location_dialog_does_not_query_without_consent_or_save_proposal(app,monkeypatch):
    from telescope_desk.sky import site
    backend=api()
    values={'latitude':50,'longitude':10,'elevation':123,'timezone':'Europe/Berlin'}
    dialog=SiteDialog(values,windows_factory=lambda parent:WindowsLocationRequest(parent,api=backend))
    monkeypatch.setattr(site.QMessageBox,'question',lambda *a,**k:site.QMessageBox.StandardButton.No)
    dialog.request_windows();assert backend.requested==0
    dialog.apply_proposal(LocationProposal(52,13,8000))
    assert dialog.lat.value()==52 and dialog.height.value()==123
    assert '8' in dialog.status.text() and values['latitude']==50
    assert not hasattr(dialog,'site')
    dialog.lon.setValue(12);dialog.validate()
    assert dialog.site.longitude==12 and values['longitude']==10
    dialog.deleteLater()


def test_cancel_preserves_existing_location_and_discards_late_result(app):
    dialog=SiteDialog({'latitude':50,'longitude':10,'elevation':123,'timezone':'Europe/Berlin'})
    dialog.reject();dialog.apply_proposal(LocationProposal(52,13))
    assert dialog.lat.value()==50 and not hasattr(dialog,'site')
    dialog.deleteLater()


def test_manual_entries_use_windows_timezone_proposal(app,monkeypatch):
    from telescope_desk.sky import site
    monkeypatch.setattr(site,'system_timezone',lambda:'America/New_York')
    dialog=SiteDialog({})
    assert dialog.zone.text()=='America/New_York'
    dialog.lat.setValue(-33);dialog.lon.setValue(151);dialog.validate()
    assert dialog.site.latitude==-33 and dialog.site.timezone=='America/New_York'
    dialog.deleteLater()


def test_seestar_location_uses_only_audited_read_and_checks_identity(monkeypatch):
    from telescope_desk.location import read_seestar_location
    from seestarpy import auth
    import socket
    calls=[]
    class Socket:
        def settimeout(self,*a):pass
        def connect(self,*a):pass
        def close(self):calls.append('closed')
    monkeypatch.setattr(socket,'socket',lambda *a,**k:Socket())
    monkeypatch.setattr(auth,'KEY_PATH',None)
    reply={'code':0,'result':{'device':{'sn':'fixture'},'location_lon_lat':[13,52]}}
    def read(sock,command):
        assert command['method']=='get_device_state'
        assert command['params']['keys']==['device','location_lon_lat']
        return reply
    monkeypatch.setattr(auth,'_send_recv',read)
    proposal=read_seestar_location(NS(ip='192.0.2.1',serial='fixture'))
    assert proposal.latitude==52 and proposal.longitude==13 and proposal.elevation is None
    reply['result']['device']['sn']='different'
    with pytest.raises(ValueError):read_seestar_location(NS(ip='192.0.2.1',serial='fixture'))
    assert calls==['closed','closed']
