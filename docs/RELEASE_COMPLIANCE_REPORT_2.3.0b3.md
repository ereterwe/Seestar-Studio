> Aktueller Ergänzungsstand nach weiterer Quellenklärung:
> [Technische Ergebnisse](TECHNICAL_LICENSE_RESOLUTION.md),
> [Codec-Fakten](CODEC_LEGAL_REVIEW.md), [Microsoft](MICROSOFT_RUNTIME_REVIEW.md).
> Der folgende Bericht bleibt die Abnahme des ursprünglichen b3-Kandidaten.

# Seestar Studio 2.3.0b3 — compliance report

8 November 2026. **Local candidate; native source/build and legal questions remain
OPEN/BLOCKER.** The owner clarified that b3 is to be created locally from b2 and
that the source update should go to the public GitHub repository. No prior b3
release exists. The earlier link request is resolved. Existing b2 files are preserved.

## A. Summary

B3 applies compliance/packaging corrections only. All 166 automated tests passed.
Nine unused Qt files are excluded with retained-import checks. Colorama 0.4.6
source/license is included; two reproducible vendor notice-path collisions are
fixed by preserving complete paths. Public-repository wording is corrected in
German and English. Audit tooling emits PASS/OPEN/BLOCKER and does not equate
archive integrity with exact native Corresponding Source.

## B. Dependencies

The new build has 130 PE binaries, compared with 139 in the unchanged b2 baseline.
Installed wheel RECORD or base-Python hashes establish local origin of third-party
files; publisher source/patch correspondence remains separate. The complete b3
file/native/PYZ evidence will be retained in `compliance/B3_BINARY_SOURCE_MAP.json`.
Forty verified upstream source archives and 205 original notices are available.
See [native review](NATIVE_COMPONENT_REVIEW.md) for the static/transitive components.

## C. Source kit

Application sources, SeestarPy sources, artwork, catalog, exact pins and build/
installer scripts are packaged with the application. Build metadata records the
application source hash. The separate upstream archive is review material, **not
complete proven Corresponding Source**. Qt/Mesa, FFmpeg/zlib, OpenSSL/Rust, codecs,
OpenBLAS and other native compiler/patch/static dependency recipes remain incomplete.
Unmodified general tools and qualifying System Libraries require documented
case-by-case treatment. Wheel reinstalls do not prove native rebuilds. A clean
external-PC rebuild and complete native source kit remain unverified.

## D. Licenses

Project: GPL-3.0-only. Dependency texts/attributions retain their original licenses.
Colorama notices and nested setuptools vendor notices are now preserved. Qt Virtual
Keyboard's GPLv3-only option was documented for the baseline and its unused chain
is excluded from b3. OpenNGC's six provenance files match; unchanged catalog data,
authors, URLs and CC BY-SA 4.0 remain distinct from application GPL licensing.
See LICENSING.md, THIRD_PARTY_NOTICES.md and [workflow](COMPLIANCE_WORKFLOW.md).

## E. Native components

Recorded facts include CPython OpenSSL 3.0.16, cryptography OpenSSL 4.0.3, FFmpeg
9.0.1 LGPL-2.1-or-later configuration, WCSLIB 8.6, Mesa embedded version indication,
Pillow codecs and NumPy BLAS configuration. Their exact source/build chains are
not automatically established by those versions. Microsoft DLL redistribution
rights and System Library classification are assessed individually, not by filename.
An isolated changed-QtCore DLL loading/widget/20-frame decoder probe passed on the
baseline. Appended overlay bytes prove acceptance of changed DLL bytes, not an
independent rebuilt Qt ABI. The new complete native EXE is tested separately.

## F. Security and tests

All reachable baseline Git blobs/commits/tags were scanned without a secret match.
Current nonignored sources, payload files, nested ZIPs and decompressed PYZ code
are scanned. Upstream example IDs/build paths remain explicit review findings.
Known user keys/APKs/profiles are excluded. No complete privacy guarantee is inferred
from pattern scans. No telescope control or movement test is part of this audit.
Historical b2 installer tests and private local report scans remain historical
in [initial report](compliance/B2_INITIAL_REPORT.md); new b3 checks are recorded
separately. No previous public artifact is overwritten.

## G. Legal questions

[ZWO interoperability review](ZWO_INTEROPERABILITY_REVIEW.md) describes the actual
PEM/APK/XAPK workflow and challenge signatures. Entitlement, necessity, terms,
protection measures and trademarks remain OPEN. Microsoft redistribution and
applicable codec patents require separate assessment. No final legal clearance
is asserted. The independence notice is preserved.

## H. Publication status

Source update to GitHub is authorized by the owner. New public binary release
uploads remain withheld pending the documented issues. BLOCKER: exact native
sources/patches/build/static-dependency correspondence. OPEN: Microsoft rights,
ZWO/codec legal review, external clean-PC rebuild and long-run hardware validation.
The old b2 notice/PDF-chain defects stay documented; b3's fixes do not silently
repair older downloads. No history rewrite or visibility change is performed.

## I. Next steps

Retain exact candidate hashes, package verification and test results; push the
reviewed source update. Obtain vendor build provenance or make controlled native
replacement builds, then assemble complete matching source delivery. Resolve the
listed legal questions before proposing a public binary release. Existing source
rights under GPL are unaffected by the project's release policy.

## Candidate verification

The full b3 build passed 166 tests in 23.54 seconds. The frozen Windows EXE
started, loaded 14,034 catalog entries, computed the synthetic-site sky view and
closed cleanly with exit 0. Control stayed disabled. This is a native application
smoke test; no telescope movement/capture test is claimed. Version, catalog hashes,
application source hash, required documents, source archive hashes and package
notice directories pass the automated checks. Native Corresponding Source remains
BLOCKER; heuristic payload review and legal/remote-delivery checks remain OPEN.

The final installer passed real local install/reinstall/start/uninstall tests:
1,443 payload files matched, exit codes were 0, shortcuts/registration were cleaned,
and personal settings/authentication configuration/session database hashes remained
unchanged. The installed frozen application also exited cleanly. These are local
Windows tests, not an external clean-PC or new hardware-observation test.

Final immutable candidate hashes are in `compliance/B3_ARTIFACTS.json`; full final
payload evidence is exported after packaging to `compliance/B3_BINARY_SOURCE_MAP.json`
and the ignored `reports/compliance-2.3.0b3/B3_FINAL_COMPLIANCE.json`. Preliminary
snapshots embedded in the ZIP are historical; post-build evidence exports are not
recursively embedded into the payload they hash. Current technical notices/source
checks pass; unresolved native source/build and legal issues remain as listed.
