"""Per-Windows-session instance marker shared with the installer."""
import ctypes
from ctypes import wintypes
import os

MUTEX_NAME = 'Local\\SeestarStudio.Main'


class InstanceLock:
    def __init__(self, name=MUTEX_NAME):
        self.handle = None
        self.already_running = False
        if os.name != 'nt': return
        self.kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        self.kernel.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        self.kernel.CreateMutexW.restype = wintypes.HANDLE
        self.kernel.CloseHandle.argtypes = [wintypes.HANDLE]
        ctypes.set_last_error(0)
        self.handle = self.kernel.CreateMutexW(None, False, name)
        if not self.handle: raise ctypes.WinError(ctypes.get_last_error())
        self.already_running = ctypes.get_last_error() == 183

    def close(self):
        if self.handle:
            self.kernel.CloseHandle(self.handle)
            self.handle = None
