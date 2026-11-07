import time
from seestar_studio.manager import TelescopeManager
from seestar_studio.models import DeviceInfo


class FakeMonitor:
    instances = []
    def __init__(self, info):
        self.info, self.running = info, False
        self.instances.append(self)
    def start(self): self.running = True
    def stop(self): self.running = False
    def native_frame(self): return None
    def snapshot(self):
        if self.info.serial == "broken":
            raise ValueError("simulated malformed telemetry")
        return {"sn": self.info.serial, "connected": self.running, "target": "simulated"}


def wait_for(predicate, seconds=4):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if predicate(): return
        time.sleep(.05)
    assert predicate()


def test_independent_devices_pause_resume_and_shutdown():
    FakeMonitor.instances = []
    records = [DeviceInfo("good", "127.0.0.1"), DeviceInfo("broken", "127.0.0.2")]
    manager = TelescopeManager(lambda: records, FakeMonitor, .2)
    manager.start()
    try:
        wait_for(lambda: len(manager.latest()[0]) == 2)
        assert manager.latest()[0]["good"][1].connected
        assert manager.latest()[0]["broken"][1].error
        manager.set_paused("good", True)
        wait_for(lambda: manager.latest()[0]["good"][1].paused)
        manager.request_scan()
        time.sleep(.7)
        assert manager.latest()[0]["good"][1].paused
        manager.set_paused("good", False)
        wait_for(lambda: manager.latest()[0]["good"][1].connected)
        records[0] = DeviceInfo("good", "127.0.0.3")
        manager.request_scan()
        wait_for(lambda: manager.latest()[0]["good"][0].ip == "127.0.0.3")
    finally:
        manager.stop()
        manager.join(5)
    assert not manager.running
    assert all(not monitor.running for monitor in FakeMonitor.instances)
