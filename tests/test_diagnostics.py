import json
import os
import uuid
import pytest
from seestar_studio.diagnostics import diagnostic_snapshot
from seestar_studio.models import DeviceInfo, Telemetry
from seestar_studio.instance import InstanceLock


def test_diagnostics_excludes_private_fields_and_error_contents():
    private = 'private-sentinel-never-export'
    info = DeviceInfo(private, private, 'Seestar S50')
    telemetry = Telemetry(private, True, values={'firmware': '9.75', 'target': private,
        'location': private, 'raw': private, 'capabilities': {'can_stack': True,
        'can_secret': private, 'serial': private}}, error=private, image_error=private)
    report = diagnostic_snapshot({private: (info, telemetry, None)}, True, private)
    assert private not in json.dumps(report)
    assert report['devices'][0]['capabilities'] == {'can_stack': True}
    assert report['devices'][0]['status_error_present'] is True


@pytest.mark.skipif(os.name != 'nt', reason='Windows mutex')
def test_instance_marker_releases_after_close():
    name = 'Local\\SeestarStudio.Test.' + uuid.uuid4().hex
    first = InstanceLock(name); second = InstanceLock(name)
    try:
        assert not first.already_running and second.already_running
    finally:
        second.close(); first.close()
    third = InstanceLock(name)
    try: assert not third.already_running
    finally: third.close()
