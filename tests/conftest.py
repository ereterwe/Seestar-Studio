import os
import socket
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# SeestarPy performs discovery during import. Unit tests must never reach
# real telescopes, including via its mDNS fallback.
with patch.object(socket.socket, "sendto", side_effect=OSError("unit test: no network")), \
     patch.object(socket.socket, "recvfrom", side_effect=OSError("unit test: no network")), \
     patch.object(socket, "gethostbyname", side_effect=socket.gaierror("unit test")):
    import seestarpy

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def app():
    instance = QApplication.instance() or QApplication([])
    yield instance
    # Exercise asynchronous window shutdown before Qt is destroyed. Otherwise
    # a still-pending catalog/history callback can race interpreter teardown.
    import time
    windows = list(instance.topLevelWidgets())
    for window in windows:
        window.close()
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        instance.processEvents()
        if not any(getattr(w, 'workers_running', lambda: False)() for w in windows):
            break
        time.sleep(.02)
    instance.processEvents()
    from PySide6.QtCore import QCoreApplication, QEvent
    import shiboken6
    for window in windows:
        if shiboken6.isValid(window): window.deleteLater()
    QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
    instance.processEvents()
    import gc
    gc.collect()
