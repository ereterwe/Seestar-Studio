# Licenses and redistribution

Seestar Studio is licensed under **GPL-3.0-only**, without warranty.
The full license is in LICENSE. The corresponding application source and build
scripts are in SeestarStudio-source.zip in the Windows folder distribution.

SeestarPy 0.8.0, copyright its contributors including Kieran Leschinski, is
GPLv3. Its installed Python sources are included unchanged in the source archive.
The adapter in seestar_studio/backend.py extends ScopeMonitor; it does not change
the installed library. Upstream: https://github.com/astronomyk/seestarpy

This software uses Qt / PySide6 / Shiboken 6.12.0, copyright The Qt Company and
contributors, under their applicable open source licenses, including LGPLv3.
Qt is dynamically linked. Replacement of the Qt/PySide6 libraries and reverse
engineering for debugging modifications to those libraries are permitted.
Use ABI-compatible replacement DLLs/modules in _internal, or rebuild from the
provided application source with your modified Qt/PySide6 build. No signature
check or technical restriction prevents replacement.

Dependency licenses are collected under licenses/ in the folder distribution.
Exact versions are recorded in dependency-versions.json and requirements-lock.txt.
Other runtime dependencies include CPython (PSF), NumPy (BSD), Pillow (HPND and
bundled third-party notices), cryptography (Apache/BSD), cffi (MIT), requests
(Apache-2.0), pysmb (zlib/libpng), and their transitive dependencies. Their own
license texts, rather than this summary, govern their use.

When redistributing binaries, preserve license/copyright notices and provide
the complete corresponding source under the applicable licenses, including
build scripts and any modifications. Publish source alongside downloadable
binaries (GPLv3 section 6), or use another compliant source-delivery method.
Do not present this private development build as a completed public distribution
without preparing the corresponding sources for its bundled third-party binary
libraries as well. The application archive alone is not that complete set.

Source and licensing references:

- GPLv3: https://www.gnu.org/licenses/gpl-3.0.html
- Qt obligations: https://www.qt.io/development/open-source-lgpl-obligations
- Qt source archives: https://download.qt.io/official_releases/qt/
- PySide source archives: https://download.qt.io/official_releases/QtForPython/
- Python source: https://www.python.org/downloads/source/

The Seestar authentication key is never included in builds, archives, source,
logs, or notices. SeestarPy continues to discover it locally at runtime.
# Sky Explorer additions

OpenNGC © Mattia Verga and contributors, CC BY-SA 4.0. Bundled catalog files,
original acknowledgements, license and immutable source provenance are in
`seestar_studio/catalog_data` (inside `_internal` in the Windows package).
Astropy and astropy-iers-data: BSD-3-Clause. PyERFA: BSD-3-Clause, with ERFA/SOFA
notices. PyYAML: MIT. Their distribution license files are in `licenses/`.


Installer built with Inno Setup 7.1.1, https://jrsoftware.org/.
Copyright (C) 1997–2026 Jordan Russell; portions (C) 2000–2026 Martijn Laan.
Original license included as licenses/INNO-SETUP-LICENSE.txt.

Qt Multimedia / FFmpeg added in V2.2: dynamically linked FFmpeg 9.0.1 from
PySide6_Addons 6.12.0. LGPL 2.1-or-later as reported by the supplied avcodec DLL.
See licenses/FFMPEG-LGPL-2.1.txt and licenses/FFMPEG-NOTICE.txt.
Complete native corresponding sources and per-file notices remain a prerequisite
for any future public distribution. No public release authorized.

## Beta additions

PyWinRT 3.2.1 (runtime, Windows.Devices.Geolocation, Windows.Foundation and
Windows.Foundation.Collections): MIT, original notices included. typing_extensions:
PSF-2.0. Windows Location is an optional operating-system service, used only after
explicit consent; Microsoft services may be involved by Windows itself.

Seestar Studio's observatory icon is an original project graphic under GPL-3.0-only;
see assets/ICON-LICENSE.txt and docs/ICON.md. No ZWO/OpenAI/third-party logo included.

Additional unchanged upstream notices are retained under licenses/upstream.
UPSTREAM_INDEX.json identifies source archives and original paths. Qt attribution
manifests: docs/QT_ATTRIBUTIONS.json. Native imports/versions: dependency-inventory.json.
Qt Virtual Keyboard uses its GPLv3 open-source option. See LICENSING.md for unresolved
binary-source correspondence and redistribution questions. No legal clearance implied.
