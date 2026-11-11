# Telescope Desk

Independent open-source Windows application for compatible ZWO Seestar telescopes.
Not affiliated with, endorsed by, or officially supported by ZWO.

Native Qt dashboard with multiple telescope views, live stacks and live video,
telemetry, file downloads, Sky Explorer, observation planning and session analysis.
German/English interface. Local-first; read-only by default. GPL-3.0-only.

Version **2.3.0b3 — draft beta**, formerly Seestar Studio. The source repository
uses the Telescope Desk name; its existing URL remains
https://github.com/ereterwe/Seestar-Studio. Telescope Desk is a provisional name;
trademark review is pending.

The current Windows beta is maintained as a GitHub draft, replacing the obsolete
2.3.0b2 draft. Draft assets are visible only to repository collaborators with access;
there is no public binary download yet. Remaining source-completeness and legal
review items are documented in [LICENSING.md](LICENSING.md).

## Features

- Independent live-stack viewers and telemetry for multiple telescopes.
- Live video, image zoom/pan, image export and full-screen display.
- Telescope file browser and downloads to local storage.
- Offline Sky Explorer, observation planning and session statistics.
- Explicitly enabled telescope controls with confirmation prompts.
- Local authentication setup and a German/English native Windows interface.

The application supplies no ZWO APK, firmware or authentication key and requires
no application account or cloud login. Optional online features are identified
separately. Existing third-party rights and license requirements still apply.

## Changes in this beta

The product, EXE, installer and Python package now use Telescope Desk. Existing
profiles remain usable. Unused Qt Multimedia Widgets and Pillow AVIF, WebP,
color-management and Tk helper branches are excluded; the working Qt/FFmpeg
Live View backend is retained. Third-party notices now use the correct product
name and source paths.

174 automated tests passed in the latest completed review. Local portable and
installed starts, installation/reinstallation/uninstallation, JPEG/PNG/RAW image
paths and payload hashes were checked. These are development-PC tests, not a
new telescope or external clean-PC certification. Details:
[Pillow and source review](docs/compliance/PILLOW_SOURCE_REVIEW.md).

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
