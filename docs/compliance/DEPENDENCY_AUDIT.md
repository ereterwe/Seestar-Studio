# Dependency audit — Telescope Desk

Installed packages are distinguished from proven bundled runtime presence. A core; B build; C test; D implemented optional feature; E proven unnecessary; F unresolved. No F component is removed.

| Package | Version | Declared license | Class | Evidence/action |
|---|---|---|---|---|
| PySide6 | 6.12.0 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | F | ambiguous shared module ownership; runtime presence not established; retain if present unless exclusion proven |
| PySide6_Addons | 6.12.0 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| PySide6_Essentials | 6.12.0 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| PySide6_Pdf | 6.12.0.140 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | F | ambiguous shared module ownership; runtime presence not established; retain if present unless exclusion proven |
| PySide6_WebEngine | 6.12.0.140 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | F | ambiguous shared module ownership; runtime presence not established; retain if present unless exclusion proven |
| PyYAML | 6.0.3 | MIT | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| Pygments | 2.21.0 | BSD-2-Clause | F | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| altgraph | 0.17.5 | MIT | B | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| astropy | 8.0.2 | BSD-3-Clause | D | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| astropy-iers-data | 0.2026.11.2.0.34.55 | BSD-3-Clause | D | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| certifi | 2026.10.23 | MPL-2.0 | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| cffi | 2.1.1 | MIT-0 | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| charset-normalizer | 3.5.2 | MIT | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| colorama | 0.4.6 | UNKNOWN | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| cryptography | 50.0.2 | Apache-2.0 OR BSD-3-Clause | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| idna | 3.20 | BSD-3-Clause | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| iniconfig | 2.3.1 | MIT | C | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| numpy | 2.5.4 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| pefile | 2024.8.26 | MIT | B | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| pillow | 13.0.0 | MIT-CMU | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| pip | 26.3 | MIT | F | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| pluggy | 1.7.0 | MIT | C | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| pyasn1 | 0.6.5 | BSD-2-Clause | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| pycparser | 3.12 | BSD-3-Clause | F | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| pyerfa | 2.0.1.5 | BSD 3-Clause License | D | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| pyinstaller | 6.22.3 | GPLv2-or-later with a special exception which allows to use PyInstaller to build and distribute non-free programs (including commercial ones) | B | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| pyinstaller-hooks-contrib | 2026.9 | UNKNOWN | B | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| pysmb | 1.2.15 | zlib/libpng | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| pytest | 9.2.0 | MIT | C | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| pywin32-ctypes | 0.2.3 | BSD-3-Clause | B | installed only; runtime presence not established, not automatically a development-only package; retain if present unless exclusion proven |
| requests | 2.34.2 | Apache-2.0 | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| seestarpy | 0.8.0 | UNKNOWN | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| setuptools | 84.2.1 | MIT | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| shiboken6 | 6.12.0 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| tqdm | 4.70.1 | MPL-2.0 AND MIT | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| typing_extensions | 4.16.0 | PSF-2.0 | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| tzdata | 2026.6 | Apache-2.0 | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| tzlocal | 5.4.5 | MIT | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| urllib3 | 2.8.0 | MIT | A | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| winrt-Windows.Devices.Geolocation | 3.2.1 | MIT | D | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| winrt-Windows.Foundation | 3.2.1 | MIT | D | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| winrt-Windows.Foundation.Collections | 3.2.1 | MIT | D | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |
| winrt-runtime | 3.2.1 | MIT | D | runtime presence evidenced by native hash or uniquely owned embedded module name; retain if present unless exclusion proven |

## Proven exclusions

- E: QtMultimediaWidgets module/DLL, added by PyInstaller hook; no QVideoWidget or QGraphicsVideoItem use. QVideoSink remains. PE regular/delay-import exclusion guard runs every build.
- E: Pillow AvifImagePlugin/_avif, outside JPEG/raw stack and jpg/jpeg/png thumbnail/export paths. Removed by module analysis, not DLL deletion.
- Historical nine Qt exclusions predate this baseline and are not counted as new removals.

Direct/transitive origin and native imports are retained in the audit JSON; dynamic plugin ownership and embedded static versions are not fully resolved. This is not a complete legal classification.
