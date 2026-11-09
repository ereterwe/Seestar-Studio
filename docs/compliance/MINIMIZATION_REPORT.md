# Telescope Desk 2.3.0b3 — local minimization result

Application source/build commit: e02ceeb172ce64acc3084f3e225a7396616a65bf.
Branch: refactor/telescope-desk-minimal-runtime. Version unchanged. Final validation
and packaging-tool follow-ups are separate local commits; the packaged source ZIP
and build-info source hash identify the exact application inputs. Main remains
b69a0b28bb78d9b4450d99eb2d5e10e33acfcd59. No push or public release performed.

## Measured comparison

| Metric | Seestar Studio baseline | Telescope Desk |
|---|---:|---:|
| Portable ZIP bytes | 88442773 | 84706875 |
| Installer bytes | 62775719 | 61082404 |
| Payload files | 1642 | 1670 |
| DLLs | 57 | 56 |
| Native files including EXE/PYD | 130 | 127 |
| FFmpeg encoder implementations | 183 | 183 |
| FFmpeg decoder implementations | 498 | 498 |

ZIP reduction: 3,735,898 bytes (4.22%).
Installer reduction: 1,693,315 bytes (2.70%).
Files increased because of retained historical evidence and new documentation.
Installed distributions inspected: 44, including build/test tools; this is not a
claim of 44 required runtime packages. Exact inferred runtime ownership and
remaining ambiguities are recorded in the SBOM/audit.

## Proven removals

- Qt6MultimediaWidgets.dll (62,264 bytes) and QtMultimediaWidgets.pyd (144,184 bytes):
  PyInstaller's extra module; no widget/video-item use. Existing QVideoSink path retained.
- Pillow _avif.cp312-win_amd64.pyd (7,893,504 bytes) and its Python plugin: unnecessary
  for the explicit RAW/JPEG stack and JPEG/PNG thumbnail/export paths. Removes the
  separate Pillow AVIF/AOM/dav1d branch, not FFmpeg AV1 support.
- Total removed native bytes: 8,099,952. Full hashes in MINIMIZATION_COMPARISON.json.
- All retained third-party native bytes match the baseline. Historical nine Qt
  exclusions predate this work and are not counted again.

## Feature preservation and validation

172 tests passed (32.60 s); targeted SBOM recheck passed after adding version checks.
Portable and installed native EXE: exit 0, clean shutdown, all six tabs available,
14,034 catalog entries, synthetic sky calculations, control disabled.
Installation/reinstallation/uninstallation: exit 0; all 1,670 installed files matched;
shortcuts/registration removed; both old/new profile configuration hashes unchanged.
Initial restricted installer invocation failed resolving LocalAppData before installation;
normal user-access run of the identical installer passed. No administrator install.

Packaged Qt/FFmpeg probe decoded 20 synthetic GIF video frames. Changed-copy Qt DLL
loaded successfully; this is not a custom Qt rebuild. Unit tests cover video workers,
reconnect/stop, multiple views, images, downloads, planning and setup behavior.
No non-name feature code changed except profile/log selection; shared legacy mutex
remains to prevent simultaneous old/new profile writers. Foreign licence texts and
catalog data remain unchanged. Old Windows artifacts are retained and hash checked.

The developer's successful real Seestar Live View test is valid baseline evidence.
Exact model/firmware/codec for that test was not supplied. This candidate has NOT
been hardware-regression-tested. No additional S50/S50 Pro or other-model claims.
Clean external Windows without Python, Windows software-rendering-only machines,
actual RTSP codec/firmware matrix and GitHub workflow execution remain unverified.

## Naming and profiles

Own namespace telescope_desk; UI/about/EXE/installer/assets use Telescope Desk.
Manufacturer names, SeestarPy and the existing repository URL stay correct.
The new name is provisional and not trademark-cleared. Installer uses a new identity.
An existing legacy profile is reused in place if no new profile exists: settings,
plans, history and authentication remain available, with no private-key copy.
Old/new process instances share the legacy mutex. Fresh profiles use new naming.

## SBOM, sources and remaining technical work

CycloneDX 1.6 file inventory covers every selected payload file with SHA256;
verification found no missing/extra/changed files or application-version mismatch.
Package metadata/native origins and actual compiled FFmpeg capabilities are recorded.
359 demuxers, 184 muxers, 32 input and 26 output protocols remain available.
The composition is explicitly incomplete for exact embedded static linkage and
ambiguous Python ownership. Therefore a fully resolved component SBOM criterion
is OPEN despite complete file coverage. Do not call it complete component clearance.

A local corresponding-source candidate contains matching app sources and 105
hash-checked upstream archives. Exact native patch/static build correspondence and
legal adequacy remain OPEN. Original upstream archives include public test fixtures;
no user/ZWO authentication files or APKs are included. This archive is not a certified
complete Corresponding Source release. Byte-identical rebuilds are not asserted
as a general GPL requirement. See the preserved licensing dossiers.

FFmpeg encoder/decoder/protocol minimization beyond these exclusions remains OPEN:
no custom compatible reduced FFmpeg was built or hardware-validated. Retain uncertain
features and Mesa/software-rendering/MSVC fallbacks. Media Foundation equivalence
for the actual RTSP streams is unproven. Backend changes do not grant patent rights.

Manual trusted-self-hosted Windows workflow is prepared: tests, build, installer,
file inventory, SBOM, source candidate and security checks; no uploads/releases.
It requires the documented compiler/source cache and has not run on GitHub.

## Remaining legal review and release gate

GPL-3.0-only applies to own code. Qt/PySide LGPL/GPL choices, FFmpeg LGPL,
Python PSF, SeestarPy GPL, permissive scientific/crypto/image libraries, OpenNGC
CC-BY-SA and Microsoft's separate runtime conditions remain relevant.

Priorities: (1) APK/RSA interoperability and authentication rights;
(2) AVC/HEVC/AV1/VP9/AAC and other remaining codec patents;
(3) Microsoft redistribution/recipient conditions;
(4) exact GPL/LGPL source/replacement evidence; (5) Telescope Desk trademark/name.
Technical file exclusion is not legal clearance. No consent replaces required rights.

Before a public beta: renewed safe Live View regression, external clean-PC test,
resolve the component/source completeness gaps, review legal issues, then explicit
owner authorization for publication. This is a usable local candidate, not a report
that every master-order acceptance criterion is finished.

Final packaging revision: caee8335bc25d4a5e875ffa009c91e8f38b1bf24 (clean tree).
The application build revision remains e02ceeb; runtime source hash is unchanged.
Final post-build reports/checksums are external evidence; documentation inside the
immutable ZIP is a packaging-time snapshot and can refer to the preceding local QA.
The later local Pillow candidate removes Tk/CMS/WebP helpers after targeted tests;
see PILLOW_SOURCE_REVIEW.md. Above measurements describe the preserved earlier
candidate, not the later build. Further static core and FFmpeg reduction remains open.
