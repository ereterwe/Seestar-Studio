# Telescope Desk — minimization work in progress

Baseline commit b69a0b28bb78d9b4450d99eb2d5e10e33acfcd59; branch
refactor/telescope-desk-minimal-runtime. Version remains 2.3.0b3.
Baseline: 169 tests pass; after namespace/profile changes: 171 tests pass.
Baseline inventory: 1,642 files, 57 DLLs, 130 native files; hashes in baseline/.

Namespace telescope_desk, executable TelescopeDesk.exe, localized product labels,
assets and build/installer entries renamed. Existing configuration, plans, history
and authentication directory are reused in place. Legacy mutex prevents concurrent
old/new writes. Fresh profiles use TelescopeDesk/Telescope Desk. Installer has a
new identity; old installations and release artifacts are retained.

Current build and post-build comparisons are pending. No new hardware validation,
no clean external Windows test, no software-rendering-only host test is claimed.
Original successful developer Live View test remains valid baseline evidence.

Open legal items: APK/RSA interoperability; codec patents; Microsoft runtime
redistribution; precise GPL/LGPL source obligations; provisional Telescope Desk name.
No publication, main push, repository rename or history rewrite is authorized.
