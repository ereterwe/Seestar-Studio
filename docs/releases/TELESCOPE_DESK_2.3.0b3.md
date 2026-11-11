# Telescope Desk 2.3.0b3 — Windows beta

Telescope Desk is the new name of Seestar Studio: an independent, local-first
Windows application for compatible ZWO Seestar telescopes. It is not affiliated
with, endorsed by or officially supported by ZWO.

## Included functionality

Native multi-telescope live-stack viewers, live video, telemetry, local file
downloads, offline Sky Explorer, observation planning, session analysis and
explicitly enabled telescope controls. German and English interfaces are available.
Read-only operation is the default. No APK, firmware or private authentication
key is included; users provide their own local authentication inputs.

## Changes since the previous draft

- Renamed application, installer, executable and Python package to Telescope Desk.
- Preserved compatibility with existing user profiles without copying keys.
- Removed unused Qt Multimedia Widgets and Pillow AVIF/WebP/CMS/Tk branches.
- Retained the existing Qt/FFmpeg Live View implementation.
- Corrected product names and paths in third-party notices and icon documentation.
- Added native-file/source mappings, supplier patch evidence and a scoped SBOM.

## Packages

- `TelescopeDesk-2.3.0b3-win64.zip`: extract the entire folder and run TelescopeDesk.exe.
- `TelescopeDesk-2.3.0b3-setup-win64.exe`: per-user Windows x64 installer.
- `TelescopeDesk-2.3.0b3-source.zip`: application source and build instructions.
- `TelescopeDesk-2.3.0b3-corresponding-source.zip`: application sources plus 105
  original upstream source archives; a candidate, not a completeness certification.
- `TelescopeDesk-2.3.0b3-SBOM.json`: selected payload inventory and component evidence.
- `TelescopeDesk-2.3.0b3-SHA256SUMS.txt`: artifact integrity checksums.

Python is not required to run the Windows packages. Unsigned Windows builds may
display reputation prompts. See INSTALLATION.md and BUILDING.md in the package.

## Validation and limitations

The replacement build was revalidated on 11 November 2026: 174 automated tests,
targeted JPEG/PNG/RAW checks, portable/installed starts, and installation,
reinstallation and removal passed. All 1,672 payload file hashes match; existing
user profiles remain unchanged. GitHub SHA-256 digests match all six uploaded assets.
S50/S50 Pro have historical hardware evidence; this replacement build has not
received a new real-telescope or clean external-PC regression test. No hardware
support claim is made for untested models.

**Draft beta — no public binary release yet.** The exact native corresponding-source
chain, remaining embedded components and legal review items are still open.
GPL-3.0-only applies to the project's own code; third-party terms remain applicable.
See LICENSING.md and docs/compliance/PILLOW_SOURCE_REVIEW.md. These files and the
source candidate do not certify legal clearance or complete Corresponding Source.
