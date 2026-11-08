# Release compliance workflow

The audit does not publish, modify a release, start Seestar Studio, discover
telescopes, or read authentication directories. Run it against the **actual
versioned payload**, not merely the current development environment:

```powershell
.\.venv\Scripts\python.exe -m tools.release_compliance --target dist/2.3.0b3/SeestarStudio --expected-version 2.3.0b3 --output reports/compliance-2.3.0b3/b3-candidate
```

B3 is newly built locally from the audited baseline. The old b2 comparison is
retained separately as historical evidence and a negative version check. An
output directory inside the inspected payload is rejected. `compliance.json`
contains all file hashes, PE origins/imports, Python archive entries, source
archive hashes and checks; `COMPLIANCE.md` is the short readable result.

Exit/status: 0/PASS for evidenced checks; 1/OPEN for incomplete evidence;
2/BLOCKER for a material failure or an incomplete audit. An exception is recorded
by type only, without potentially sensitive message text. A source archive hash
PASS proves archive integrity, **not** binary/source correspondence. Current
native build correspondence deliberately remains a BLOCKER. No automated result
constitutes a legal opinion or publication approval.

The checker reads installed package RECORD hashes without importing package code.
Matching a payload DLL to that RECORD proves local provenance. It does not prove
the wheel publisher's identity, exact upstream patches or reproducibility. Python
module owners are matched against individual installed source records, avoiding
the false inference that every package sharing the PySide6 namespace is shipped.
PYZ modules and nested ZIPs are scanned after decompression; arbitrary extracted
files are never executed. Archive limits produce OPEN, not PASS. Scans identify
patterns without echoing matching values. Heuristic results require review;
personal coordinates cannot be exhaustively distinguished from catalog/test data.

Git scans cover locally reachable blobs, commits and annotated tags, including
fetched refs. Unreachable objects, un-fetched remote refs, LFS and server-side
copies require separate review. Current tracked/nonignored files are scanned
separately. Ignored local profiles/logs are not build inputs; manual disclosure of
them is a separate risk. This does not silently treat an uninspected installer,
public asset or tester copy as checked.

## Library replacement and package reduction

The onedir layout contains separate Qt/FFmpeg DLLs and bindings. For your own
compatible build, copy the entire application to a writable test directory,
retain an original backup, then replace the matching x64 Qt module DLLs and their
matching plugins/PySide6/Shiboken bindings as required by their ABI. Preserve the
`_internal/PySide6` layout. Rebuild the application from the matching source if
the replacement ABI differs. Do not mix random Qt major/minor builds or MS runtimes.
Preserve your modifications, build options and notices for redistribution.
Reverse engineering to debug modifications to LGPL components is not prohibited
by this project. Upstream source/build links are in DEPENDENCY_SOURCES.json;
missing exact native build recipes remain recorded in the compliance report.

The following technical probe uses a **copy**, never the installed application:

```powershell
.\.venv\Scripts\python.exe -m tools.qt_compliance_probe --target dist/2.3.0b2/SeestarStudio --output reports/compliance-2.3.0b3
```

It excludes nine unused Qt Virtual Keyboard/QML/Quick/PDF files, checks retained
PE imports (including delay imports), appends a harmless overlay to copied QtCore,
and verifies the actual loaded DLL paths/hashes, native widget rendering and
local synthetic-video decoding. It uses matching installed Python helper scripts
because frozen scripts live in PYZ. It is **not** a complete EXE regression test,
an independently rebuilt replacement Qt, a hardware test or proof that every
LGPL obligation is satisfied. Those limits are part of its machine report.

The spec now applies the same explicit exclusion and fails if a future retained
binary imports an excluded library. Qt Multimedia/FFmpeg and normal image codecs
remain. Candidate EXE/installer rebuilding and smoke tests use the local b3 source; existing downloads are never overwritten by audit.

## Source kit and build evidence

Keep exact application source plus build/installer scripts; use the matching
lock file, Python x64 version and compiler/toolchain records. Include native
library sources, patches, configuration and required static dependencies, subject
to documented applicable exceptions. `requirements-lock.txt` alone reinstalls
wheels; it does not rebuild native libraries from their sources. Existing source
archives and successful application builds do not close missing native recipes.

Publish matching source through an applicable GPLv3 section 6 delivery method
when binaries are conveyed. Repository visibility alone does not identify a
binary's corresponding source. General unmodified build tools may qualify for
the GPL source exception; their embedded runtime portions need separate analysis.
Windows OS interfaces, bundled Microsoft redistributables, third-party DLLs and
statically linked code must not be conflated as “system libraries.”

Authoritative references: [GPLv3](https://www.gnu.org/licenses/gpl-3.0.html),
[LGPLv3](https://www.gnu.org/licenses/lgpl-3.0.html),
[Qt obligations](https://www.qt.io/development/open-source-lgpl-obligations).
