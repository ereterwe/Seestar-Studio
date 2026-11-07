"""Private local storage. Windows uses an explicit protected DACL, not chmod."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import stat


def protect(path):
    path = Path(path)
    if path.is_symlink() or getattr(path.lstat(), 'st_file_attributes', 0) & 0x400:
        raise OSError('Private storage must not be a reparse point')
    if os.name != 'nt':
        path.chmod(0o700 if path.is_dir() else 0o600)
        return
    adv = ctypes.WinDLL('advapi32', use_last_error=True)
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    ptr = ctypes.c_void_p
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.LocalFree.argtypes = [ptr]; kernel.LocalFree.restype = ptr
    adv.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]
    adv.GetTokenInformation.argtypes = [wintypes.HANDLE, ctypes.c_int, ptr, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    adv.ConvertSidToStringSidW.argtypes = [ptr, ctypes.POINTER(wintypes.LPWSTR)]
    adv.ConvertStringSecurityDescriptorToSecurityDescriptorW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(ptr), ctypes.POINTER(wintypes.DWORD)]
    adv.GetSecurityDescriptorDacl.argtypes = [ptr, ctypes.POINTER(wintypes.BOOL), ctypes.POINTER(ptr), ctypes.POINTER(wintypes.BOOL)]
    adv.SetNamedSecurityInfoW.argtypes = [wintypes.LPWSTR, ctypes.c_int, wintypes.DWORD, ptr, ptr, ptr, ptr]
    adv.SetNamedSecurityInfoW.restype = wintypes.DWORD
    token, length = wintypes.HANDLE(), wintypes.DWORD()
    descriptor, sid_text = ptr(), wintypes.LPWSTR()
    try:
        if not adv.OpenProcessToken(kernel.GetCurrentProcess(), 8, ctypes.byref(token)):
            raise ctypes.WinError(ctypes.get_last_error())
        adv.GetTokenInformation(token, 1, None, 0, ctypes.byref(length))
        data = ctypes.create_string_buffer(length.value)
        if not adv.GetTokenInformation(token, 1, data, length, ctypes.byref(length)):
            raise ctypes.WinError(ctypes.get_last_error())
        sid = ctypes.cast(data, ctypes.POINTER(ptr))[0]
        if not adv.ConvertSidToStringSidW(sid, ctypes.byref(sid_text)):
            raise ctypes.WinError(ctypes.get_last_error())
        # Current user and SYSTEM only. Inherit only into our private directory.
        flags = 'OICI' if path.is_dir() else ''
        sddl = f'D:P(A;{flags};FA;;;{sid_text.value})(A;{flags};FA;;;SY)'
        if not adv.ConvertStringSecurityDescriptorToSecurityDescriptorW(sddl, 1, ctypes.byref(descriptor), None):
            raise ctypes.WinError(ctypes.get_last_error())
        present, defaulted, dacl = wintypes.BOOL(), wintypes.BOOL(), ptr()
        if not adv.GetSecurityDescriptorDacl(descriptor, ctypes.byref(present), ctypes.byref(dacl), ctypes.byref(defaulted)) or not present.value or not dacl:
            raise OSError('Private DACL unavailable')
        result = adv.SetNamedSecurityInfoW(str(path), 1, 0x80000004, None, None, dacl, None)
        if result: raise ctypes.WinError(result)
    finally:
        if descriptor: kernel.LocalFree(descriptor)
        if sid_text: kernel.LocalFree(ctypes.cast(sid_text, ptr))
        if token: kernel.CloseHandle(token)


def private_directory(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    protect(path)
    return path


def write_new_private(path, content):
    """Exclusive creation; protect the empty file before writing secret bytes."""
    path = Path(path)
    private_directory(path.parent)
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, 'O_BINARY', 0), 0o600)
    try:
        with os.fdopen(descriptor, 'wb') as output:
            protect(path)
            output.write(content); output.flush(); os.fsync(output.fileno())
    except Exception:
        # Only the fresh file created by this call is removed on failure.
        path.unlink(missing_ok=True)
        raise
    return path
