# Pillow reduction and source traceability — 2026-11-09

Scope: local Telescope Desk 2.3.0b3 candidate on
`refactor/telescope-desk-minimal-runtime`. No upload or public release.
The previous candidate and its evidence remain intact. This report supersedes
the earlier statement that all additional Pillow pruning is pending.

## Actual reduction

The application's SeestarPy image path decodes JPEG or numeric 16-bit RAW.
SeestarPy's monitor encodes JPEG. File-manager thumbnails accept jpg/jpeg/png;
the native viewer/export path uses Qt. No application/SeestarPy caller requires
Pillow ImageTk, ImageCms or WebP. Exclusions happen during PyInstaller module
analysis, not by deleting binaries after building.

| Removed from this candidate | Uncompressed bytes |
|---|---:|
| PIL._imagingcms (and ImageCms Python module) | 275,456 |
| PIL._imagingtk (and ImageTk Python module) | 14,336 |
| PIL._webp (and WebPImagePlugin Python module) | 415,744 |
| Total additional native reduction | 705,536 |

The previously excluded Pillow AVIF branch stays excluded. Only PIL._imaging
remains as a Pillow native extension. Native file count drops from 127 to 124.
All retained DLL/PYD bytes match the previous candidate; application code is unchanged.
This removes Pillow's Little CMS/WebP/Tk branches, not Qt's separate WebP plugin.
FFmpeg and its compiled codec capabilities are unchanged.

Further removal of TIFF/OpenJPEG from the shared Pillow core would require a
separate custom Pillow build and regression validation. Deleting Python plugins
does not remove statically embedded codec code. That work is not claimed here.

## Sources and embedded components

`PILLOW_REVIEW_SOURCE_MAP.json` binds every actual native file SHA256 to its
installed-package origin and candidate source archives. All 105 downloaded
archives were checked against `docs/DEPENDENCY_SOURCES.json`.

* 111 native files have source candidates.
* The EXE contains the application's code and the PyInstaller bootloader.
* 12 Microsoft runtime files are identified separately; they are proprietary
  redistribution components, not missing open-source archives.
* No native file remains uncategorized. This is not a claim that all static
  components or exact publisher build inputs are resolved.

QtCore/QtGui/QtNetwork/QtWidgets Python bindings now map to pyside-setup.
QtMultimedia/QtSvg Python bindings also map to pyside-setup, whereas their Qt DLLs
map to qtmultimedia/qtsvg. A regression test prevents conflating those sources.

Pillow's original supplier SBOM is preserved unchanged. Its dependency closure
is scoped to the actual retained extension, excluding unavailable libimagequant
and XCB features. The retained source mapping is:

| Component | Version | Original source archive |
|---|---|---|
| Pillow core/build recipes | 13.0.0 | Pillow-git-13.0.0.tar.gz |
| libjpeg-turbo | 3.2.0 | libjpeg-turbo-3.2.0.tar.gz |
| libtiff | 4.7.2 | tiff-4.7.2.tar.gz |
| OpenJPEG | 2.5.4 plus supplier patch | openjpeg-2.5.4.tar.gz |
| zlib-ng (supplier SBOM calls it zlib) | 2.3.3 | zlib-ng-2.3.3.tar.gz |

The source map contains original Windows build recipes/dependency versions,
archive URLs, hashes and supplier license declarations. It does not replace the
original license texts bundled with the application.

The OpenJPEG patch is retained in the generated CycloneDX SBOM (`pedigree`),
including its base64 diff. Previously this detail was dropped when copying scoped
component records. Patch SHA256:
`6b0a9250ec038826a811a7eb6ea1aa59abf42d6d562042cdfddb29c7ad98ef4e`.
`git apply -p0 --check` and application to a disposable copy of upstream j2k.c
both succeed. Before/after hashes are in the source map. The supplier SBOM has
an ancestor-name typo (`libtiff` under OpenJPEG); the original is not silently
rewritten. Purl/version/diff identify OpenJPEG.

## Verification

* 174 automated tests pass, including scoped SBOM patch retention and source-family mapping.
* The rebuilt EXE's frozen module table contains none of the excluded Pillow modules.
* The actual packaged Pillow native core passes six JPEG cases (three dimensions,
  baseline/progressive), PNG round trips, RGB/Bayer RAW, SeestarPy JPEG encoding
  and rejection of corrupt JPEG input.
* This payload probe uses matching installed Pillow Python helpers and development
  Qt/NumPy. Its scope is explicit; it is not a clean-PC or complete frozen-app test.
* Portable and installed native EXEs start, calculate the local sky/catalog and
  close with exit code 0. No telescope is connected during these checks.
* Installation, reinstallation and uninstallation pass. All 1,670 installed payload
  files match; existing user profiles remain unchanged; QA registration and shortcuts
  are removed. This is a test on the development PC, not a clean external PC.
* The new SBOM covers all 1,670 payload files without hash/version discrepancies.
  Three extra documentation files offset the three removed native files in this total.
* Previous release artifact hashes are unchanged. 123 retained DLL/PYD files
  match the prior candidate byte-for-byte. Source/payload/archive scans found no
  new secret-pattern blocker; remaining compliance review states are preserved.
* Post-packaging application/installer results and artifact hashes are recorded in
  `PILLOW_REVIEW_RESULTS.json`. This external evidence postdates the immutable
  documentation snapshot inside the packaged ZIPs.

Local output directory: `release/pillow-review-2.3.0b3/`.
Portable ZIP: 84,404,436 bytes; installer: 60,969,510 bytes.
The corresponding-source candidate includes the application source and 105 original
archives. Its filename does not certify completeness: the native corresponding-source
release gate remains BLOCKER pending the outstanding source/build evidence.
Packaging revision: `2048f54d4dd64f58aa11e57c2cffa57a389684a6` (clean tree).

Reproduce with the commands below (PowerShell, repository root):

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m PyInstaller --clean --noconfirm --distpath dist/pillow-review-2.3.0b3 --workpath build/pillow-review-2.3.0b3 TelescopeDesk.spec
.\.venv\Scripts\python.exe -m tools.pillow_payload_probe --target dist/pillow-review-2.3.0b3/TelescopeDesk --output reports/pillow-review/payload-test.json
.\.venv\Scripts\python.exe -m tools.source_traceability --target dist/pillow-review-2.3.0b3/TelescopeDesk --output docs/compliance/PILLOW_REVIEW_SOURCE_MAP.json
```

## Explicit remaining gaps

No new telescope hardware test, external clean-PC test or full native rebuild.
Source candidates plus supplier recipes do not prove the exact producing build
or every statically linked component. Qt/Mesa patch/build correspondence, broader
embedded dependency closure and Microsoft redistribution conditions remain open
as described in the existing dossiers. Technical reduction does not resolve
codec patent, authentication or trademark questions. Public distribution is not cleared.
