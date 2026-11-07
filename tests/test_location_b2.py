import time
import pytest
from seestar_studio.location import WindowsLocationRequest
from seestar_studio.sky.site import SiteDialog
from tests.test_location import api, Operation, position


@pytest.mark.parametrize('permission,status,expected', [(2,0,'denied'),(2,3,'disabled'),(1,3,'disabled'),(1,5,'unsupported'),(0,0,'failed')])
def test_specific_access_statuses(app,permission,status,expected):
    backend=api(permission);backend.location_status=status
    request=WindowsLocationRequest(api=backend);errors=[];request.failed.connect(errors.append)
    request.start();request.poll()
    assert errors==[expected] and request.operation is None and not request.timer.isActive()
    request.deleteLater()


@pytest.mark.parametrize('status,expected', [(2,'no_data'),(0,'failed')])
def test_failed_position_does_not_invent_permission_error(app,status,expected):
    backend=api();backend.location_status=status
    backend.get_geoposition_async_with_age_and_timeout=lambda *a:Operation(status=3)
    request=WindowsLocationRequest(api=backend);errors=[];request.failed.connect(errors.append)
    request.start();request.poll();request.poll()
    assert errors==[expected]
    request.deleteLater()


def test_timeout_and_hresult_classification(app):
    request=WindowsLocationRequest(api=api());errors=[];request.failed.connect(errors.append)
    request.start();request.deadline=time.monotonic()-1;request.poll()
    assert errors==['timeout']
    for code,expected in [(0x80070005,'denied'),(0x800705b4,'timeout'),(123,'failed')]:
        exc=OSError();exc.hresult=code
        assert request.classify_error(exc)==expected
    request.deleteLater()


@pytest.mark.parametrize('raises', [False, True])
def test_settings_uri_explicit_only_retry_and_failed_open(app,monkeypatch,raises):
    from seestar_studio.sky import site
    backend=api(2);calls=[]
    dialog=SiteDialog({},windows_factory=lambda parent:WindowsLocationRequest(parent,api=backend))
    dialog.show();app.processEvents()
    monkeypatch.setattr(site.QMessageBox,'question',lambda *a,**k:site.QMessageBox.StandardButton.Yes)
    monkeypatch.setattr(site.QDesktopServices,'openUrl',lambda url:calls.append(url.toString()) or True)
    try:
        assert not dialog.location_settings.isVisible() and backend.requested==0
        dialog.request_windows();dialog.windows.poll()
        assert dialog.location_settings.isVisible() and calls==[] and backend.requested==1
        dialog.location_settings.click()
        assert calls==['ms-settings:privacy-location'] and backend.requested==1
        assert dialog.isVisible() and not hasattr(dialog,'site')
        # Simulated permission change by the user, no real settings touched.
        backend.request_access_async=classmethod(lambda cls:Operation(1))
        dialog.request_windows();dialog.windows.poll();dialog.windows.poll()
        assert dialog.source is not None and not dialog.location_settings.isVisible()
        dialog.show_windows_error('disabled')
        def fail_open(url):
            if raises: raise OSError('unlogged system error')
            return False
        monkeypatch.setattr(site.QDesktopServices,'openUrl',fail_open)
        dialog.location_settings.click()
        assert 'Windows-Einstellungen' in dialog.status.text()
        assert dialog.windows.operation is None
        dialog.manual();dialog.lat.setValue(40);dialog.validate()
        assert dialog.site.latitude==40
    finally:dialog.reject();dialog.deleteLater()


def test_error_messages_language_switch_and_manual_fallback(app,monkeypatch):
    from seestar_studio import i18n
    controller=i18n.TranslationController(app,'de');dialog=SiteDialog({});dialog.show()
    try:
        for code in ('denied','disabled','no_data','failed','timeout','unsupported'):
            dialog.show_windows_error(code);controller.set_language('en')
            assert dialog.status.text()==i18n.RESOURCES['location.'+code]['en']
            assert dialog.location_settings.text()=='Open Windows Location Settings'
            assert dialog.location_settings.isVisible()==(code in ('denied','disabled'))
            controller.set_language('de')
            assert dialog.status.text()==i18n.RESOURCES['location.'+code]['de']
        dialog.manual();assert not dialog.location_settings.isVisible()
        dialog.lon.setValue(-70);dialog.validate();assert dialog.site.longitude==-70
    finally:
        dialog.reject();dialog.deleteLater();controller.timer.stop();app.removeEventFilter(controller);controller.deleteLater()


def test_missing_projection_is_not_permission_denied(app,monkeypatch):
    import builtins
    original=builtins.__import__
    def missing(name,*args,**kwargs):
        if name=='winrt.windows.devices.geolocation':raise ImportError('test fixture')
        return original(name,*args,**kwargs)
    monkeypatch.setattr(builtins,'__import__',missing)
    request=WindowsLocationRequest();errors=[];request.failed.connect(errors.append)
    request.start();assert errors==['unsupported'] and request.operation is None
    request.deleteLater()
