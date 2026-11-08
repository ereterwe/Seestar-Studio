# Telescope Desk

Independent open-source Windows application for compatible ZWO Seestar telescopes.
Not affiliated with, endorsed by, or officially supported by ZWO.

Native Qt dashboard with multiple telescope views, live stacks and live video,
telemetry, file downloads, Sky Explorer, observation planning and session analysis.
German/English interface. Local-first; read-only by default. GPL-3.0-only.

Version 2.3.0b3, renamed local candidate. Telescope Desk is a provisional name;
trademark review is pending. Repository URL remains https://github.com/ereterwe/Seestar-Studio.
No public binary release is authorized by this refactor.

## Run and build

Windows x64 / Python 3.12: install requirements-lock.txt in .venv, then start.ps1.
Build with build.ps1, followed by build-installer.ps1. Portable users extract the
entire TelescopeDesk folder and run TelescopeDesk.exe; Python is not required.
See BUILDING.md and INSTALLATION.md. Existing Seestar Studio profiles are reused
in place when no Telescope Desk profile exists; no authentication key is copied.
New installations use the new product name and independent installer identity.

## Validation and compatibility

S50 and S50 Pro have historical hardware tests. The developer confirmed working
Live View on a real Seestar; exact model/firmware/codec for that test is unspecified.
A renewed hardware regression for this build remains pending. Other models are
not claimed hardware-tested. Refer to COMPATIBILITY.md and the current
[technical report](docs/compliance/MINIMIZATION_REPORT.md).

Technical cleanup is not legal clearance. APK/RSA interoperability, codec patents,
Microsoft redistribution and native source obligations remain documented in
LICENSING.md. The application supplies no user APK, firmware or private key.
