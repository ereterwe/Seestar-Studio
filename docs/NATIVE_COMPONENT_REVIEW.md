# Native component review — b2 baseline, 8 November 2026

The following sections retain the initial b2 baseline findings. B3 was subsequently
built and verified locally; no external b3 link is pending. Current closure and
remaining evidence gaps are recorded in [TECHNICAL_LICENSE_RESOLUTION.md](TECHNICAL_LICENSE_RESOLUTION.md).
Publisher-wheel/CPython comparisons, supplier SBOMs and original Qt/BLAS/CPython
build recipes supersede the earlier origin-only assessment. Old PDF/Virtual
Keyboard findings concern the preserved baseline, not the current b3 payload.

## Qt, PySide6 and Shiboken

The baseline has Qt Core, Gui, Widgets, Network, OpenGL, Svg, Multimedia and
MultimediaWidgets; plugins for Windows/platforms, styles, TLS, network information,
images, icons, generic input and media. It also pulls in unused Virtual Keyboard,
QML/Quick and PDF. Original module licenses and the third-party attributions must
be considered separately. Qt Virtual Keyboard uses the GPLv3 option, not LGPL.
The project is GPL-3.0-only; GPLv3-only Qt content is not intrinsically a conflict.
For modules offering LGPLv3, retain that option's notices and replacement rights.
See [Qt licensing](https://doc.qt.io/qt-6/licensing.html) and
[Virtual Keyboard](https://doc.qt.io/qt-6/qtvirtualkeyboard-index.html).

The baseline's `Qt6Pdf.dll` matches **PySide6_Pdf 6.12.0.140**, with PE resource
6.140.0.0. Do not label it an exact match to qtbase 6.12.0 sources. Its source/build
chain is missing. The new local spec excludes this unused plugin chain and the
Virtual Keyboard chain (nine files). This changes future packages only. The old
payload and its audit obligations remain intact. A Widgets/codec/replacement probe
passed; the rebuilt b3 application and installer passed their documented checks.

The 98 collected Qt attribution manifests also include examples and tools. Their
presence does not prove that every listed third-party component is linked. Module
sources are present for the principal 6.12.0 families, but precise enabled-feature,
embedded-library and publisher-patch mapping is OPEN. Do not replace it with a
blanket LGPL declaration. The separate Mesa software renderer is discussed below.

The installed Qt wheels' dist-info license files contain a commercial-license
reference, while their METADATA declares LGPL/GPL choices. Original open-source
license texts were collected separately from upstream sources. A missing
commercial-reference directory (such as the old PDF package's) is a packaging
inventory finding, not a conclusion that a commercial Qt contract is required.
Actual selected module options, notices and source delivery remain the test.

## FFmpeg

The five shipped DLLs match installed PySide6_Addons RECORD hashes. Runtime exports
report **FFmpeg 9.0.1**, with LGPL version 2.1 or later. Configuration is identical
in the inspected libraries and includes shared linking, disabled static FFmpeg
libraries, MSVC, enabled zlib, no `--enable-gpl` and no `--enable-nonfree`.
`--disable-static` does not prove that dependencies such as zlib are dynamic.
The configuration names **zlib 1.3.1**; exact zlib linkage/patch/build correspondence
is not established. The complete observed configure line is retained in
`compliance/NATIVE_RUNTIME_EVIDENCE.json`, without developer/user profile paths.

Against the [FFmpeg checklist](https://www.ffmpeg.org/legal.html): dynamic DLLs,
unobfuscated library names, LGPL text, About-dialog acknowledgement and absence of
project reverse-engineering restrictions are evidenced. The n9.0.1 source archive
exists and its local hash is known. Exact source/patch correspondence and complete
compiler/dependency recipe are **BLOCKER**, not proven by the tag name or configure
string. Same-server source delivery and links on the actual b3 download page are
OPEN until that release is inspected. No binary is uploaded by this audit.

The enabled native decoders may implicate patents in relevant jurisdictions;
that is a separate OPEN question, not closed by a software-license check. Obtain
the publisher's matching source/patch/build material or perform and document a
controlled replacement build with deliberately selected codecs and dependencies.

## Other native and embedded dependencies

| Component | Observed evidence | Source/license follow-up |
|---|---|---|
| CPython 3.12.10 | 27 matching base-installation binaries including stdlib extensions/dependencies; PSF license packaged | Exact installer origin and native dependency recipes not yet a complete source chain |
| CPython OpenSSL | DLLs/runtime report 3.0.16 | Apache-2.0 notices and exact source/build delivery; separate from cryptography |
| cryptography 50.0.2 | `_rust.pyd` matches RECORD; runtime OpenSSL **4.0.3** | Apache/BSD wrapper choice; embedded OpenSSL/Rust licenses and matching sources/build flags still incomplete |
| Rust crates | cryptography source `Cargo.lock` lists 40 packages; no vendored crate source tree found | Lock/checksums identify candidates, not active feature/link set or delivered source; BLOCKER for complete source-kit claim |
| NumPy 2.5.4 | Compiled extensions/BLAS DLL match wheel RECORD; compiler metadata MSVC 19.44.35229 | Preserve nested notices, build recipe and transitive static components |
| scipy-openblas | **0.3.34.106.0**, 64-bit integers, dynamic architecture | Exact OpenBLAS/LAPACK sources and wheel patches needed; BSD notices and GCC runtime exception included in NumPy notices |
| Pillow 13.0.0 | MIT-CMU license with extensive bundled notices; feature versions queried | Exact enabled codec/static dependency sources/build remain OPEN |
| Pillow codecs | FreeType 2.14.3, WebP 1.6.0, AVIF 1.4.2, libjpeg-turbo 3.2.0, OpenJPEG 2.5.4, TIFF 4.7.2, zlib-ng 2.3.3; lcms API reports 2.19 | Notices additionally identify Brotli 1.2.0, HarfBuzz 14.5.0, lcms2 2.19.1, libpng 1.6.58, xz 5.8.4. Notice inclusion alone does not prove every component is active. AV1 backend selection needs proof |
| Mesa `opengl32sw.dll` | Wheel RECORD match; embedded string **Mesa 11.2.2** | This string is not a build-provenance certificate. Exact source, patches, build and notices need confirmation; BLOCKER |
| SQLite | Runtime **3.49.1** | Public-domain status is not a source/build-correspondence proof; CPython dependency recipe needed |
| libffi, bzip2, xz, Expat etc. | CPython dependencies/imports or source candidates | Identify exact static versions and upstream notices instead of assuming the CPython version covers them |
| Astropy 8.0.2 | 18 native extensions matched; source archive and nested notices present | cfitsio/Expat/WCSLIB build correspondence still requires enabled build configuration |
| WCSLIB | Runtime **8.6**, LGPL notice present in Astropy | Matching vendored source and modifications must be tied to wheel build |
| PyERFA 2.0.1.5 / ERFA / SOFA | Extension match; BSD/ERFA/SOFA notices retained | Do not substitute app GPL for upstream notices; exact ERFA build source correspondence OPEN |
| IERS data | Package 0.2026.11.2.0.34.55, BSD notice/data source package present | Distinguish data version from astronomy code; offline operation does not change license |
| Colorama 0.4.6 | Actual frozen runtime module, previously omitted from packaging's explicit notice/source list | Locally corrected list; publisher-hash-verified sdist and original license collected. Existing b2 downloads unchanged |
| PyInstaller 6.22.3 | Embedded bootloader/runtime hooks, source archive and license/exception available | Bootloader exception is not blanket exemption of all bundled application libraries |
| Inno Setup 7.1.1 | Original license available; previous real installer test exists | Build compiler is a general tool; embedded installer runtime source/recipe review remains separate |

## Microsoft and system-library classification

Bundled files are individually identified by hash and PE version. Observed runtime
families include Python's VCRUNTIME 14.42.34438, Qt/Shiboken MSVC 14.44.35211,
NumPy's renamed MSVCP 14.40.33810 and PyWinRT's MSVCP 14.29.30157. These are
**separately shipped redistributables**, not simply Windows system files. Their
origin through a wheel or Python installer does not by itself establish our
redistribution entitlement. Check the corresponding license and REDIST list,
including rights of the entity making the distribution. No unsafe deduplication
or DLL removal was performed just to simplify licensing.

Windows-provided imports such as kernel32/user32 and API-set interfaces are a
different category: OS implementation, not copied into this payload. A GPLv3
System Library assessment depends on the section 1 criteria and the role of each
component. The C/C++ runtime/compiler relationship is a possible basis requiring
documented analysis; it does not itself grant Microsoft's redistribution rights.
Qt, FFmpeg, OpenSSL, Mesa, OpenBLAS and application-specific bindings are not
classified as exempt merely because their filenames end in DLL.

If authorized distribution of the official Microsoft redistributable installer
is preferable, select its supported x64 version, preserve its license, verify
signature, and design for installation privilege/offline constraints. This audit
does not silently add an admin requirement to the per-user portable application.
References: [Microsoft REDIST](https://learn.microsoft.com/en-us/visualstudio/releases/2022/redistribution),
[DLL selection](https://learn.microsoft.com/en-us/cpp/windows/determining-which-dlls-to-redistribute?view=msvc-170).

## Catalog and other resources

All six OpenNGC provenance-manifest files match their recorded SHA256. Snapshot
`be3cd6c5498806a2fbb2f7e0452ef802dbb02be0`, authors, upstream README, source URLs
and CC BY-SA 4.0 text are retained. The shipped CSVs are unchanged. The catalog is
a separate data work under its original license; program GPL does not relicense
it. If modified data are distributed, record changes and apply the applicable
attribution/share-alike requirements. Original app artwork remains GPL-3.0-only.

## Nested Python notices

Setuptools contributes 32 frozen vendor modules from the backports, jaraco,
more_itertools, packaging, tomli and wheel families. The old packager collapsed
nested `*.dist-info/LICENSE` paths into the same destinations: two destination
collisions were reproduced. The corrected `notice_relative_path` keeps the
complete vendor path, with zero collisions in the installed setuptools records.
This is a separate concrete notice defect in the old packaging, in addition to
Colorama. Exact versions/notices for each embedded vendor remain associated with
the setuptools source/metadata; merely including its top-level MIT license is
not a substitute. The current source archive contains upstream sources, but old
binary notice bundles are not silently repaired by this local change.
