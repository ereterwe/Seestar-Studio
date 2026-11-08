# Telescope Desk installation

This is a local beta candidate; public release authorization is still pending.
Windows x64. End users need no Python or Visual Studio installation.

Portable: extract the complete TelescopeDesk-2.3.0b3-win64.zip and run
TelescopeDesk/TelescopeDesk.exe. Keep the whole folder, including _internal.
Installer: TelescopeDesk-2.3.0b3-setup-win64.exe installs per user with no requested
administrator elevation, Start menu entry and optional desktop shortcut.
Unsigned builds may trigger Windows reputation prompts.

The installer has its own Telescope Desk identity and does not uninstall Seestar
Studio. Both applications share an instance lock to avoid concurrent profile writers.
If no new profile exists, Telescope Desk reuses the existing Seestar Studio profile
in place, including language, plans, history and authentication. It never copies the
private key. Fresh profiles use TelescopeDesk/Telescope Desk in the user profile.
Uninstalling the application preserves settings and observations.

Existing authentication can be reused. The local setup wizard can import a user's
own PEM/APK/XAPK; no APK or ZWO key is supplied and no automatic APK download occurs.
Rights to obtain/analyze the file and authenticate remain a separate legal question.
READ ONLY is the default. Existing confirmation requirements for control remain.

Local installation/reinstallation/uninstallation passed; a clean foreign PC without
Python/developer tools has not yet been verified. See the current minimization report.
