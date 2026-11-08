# Historical initial audit, superseded by local b3 build clarification

# Release compliance report — requested version 2.3.0b3

**Interim audit, 8 November 2026. Overall status: BLOCKER / b3 identity pending.**
The project owner confirms that b3 exists and has announced a link. It has not yet
been supplied. The repository/release query and local files available to this
audit show b2. This report never substitutes b2 evidence for a verified b3 release.
It is not a legal opinion, release approval or claim of complete corresponding source.

## A. Summary and verified state

The repository [ereterwe/Seestar-Studio](https://github.com/ereterwe/Seestar-Studio)
is **public**. The initial authenticated API snapshot at 09:39 UTC showed only a
b2 draft, release ID 437899425, without a publication timestamp; Actions runs and
Actions artifacts were both empty. Local main and fetched origin/main matched
`34415f5809f6d66ca89c3c5eeb88ff1946b54b85`; fetched tag `v2.3.0b2` points there.
The draft used GitHub's `untagged-8f2b22672c45aa0b2641` identifier. No b3 tag or
public b3 asset was found in that query. This is a timestamped observation, not
a denial of the owner's report of a release elsewhere or later.
The subsequent read-only refresh gave the same result; its exact timestamp and
minimal state are retained in [RELEASE_STATE.json](compliance/RELEASE_STATE.json).

| Distribution state | Evidence/status |
|---|---|
| Public source repository | Verified public at initial query |
| Public b3 release | OPEN — owner confirms existence; link/asset comparison pending |
| Visible GitHub release entry | Verified b2 draft, not a published binary release |
| Local distribution | b2 onedir, portable, installer, app-source and upstream-source archives |
| Files already supplied to testers | OPEN — no recipient-side file/hash inventory supplied |
| Changes in this audit | Local documentation/checker/packaging preparation only; not pushed or uploaded |

Closed technical checks on the available baseline: complete 1,423-file payload
hash inventory; all 138 third-party native files match installed RECORD or base
Python bytes; original application source hash matches build metadata; all six
OpenNGC provenance files match; all reachable Git objects were pattern-scanned;
portable ZIP contents equal the onedir payload. Source archive integrity and
native source correspondence are explicitly separate checks.

Local corrections: Colorama source/license collection, collision-free vendored
license paths (two old destination collisions verified), exclusion of nine unused
Qt files with dependency guards, public-repository text corrections, and a tested
PASS/OPEN/BLOCKER audit tool. An isolated Windows Qt/FFmpeg probe rendered a widget
and decoded 20 synthetic frames after exclusions and with changed QtCore bytes.
No telescope was contacted by that probe; no hardware test is claimed here.

### Unchanged baseline artifact hashes

| File (under `release/`) | SHA256 |
|---|---|
| SeestarStudio-2.3.0b2-win64.zip | `92c994a6640d1a40bb2f6f06b406185875fb88d28e6b9c68c75f6c77361e7387` |
| SeestarStudio-2.3.0b2-setup-win64.exe | `c34775f88b84803a2e805d26da5d29f545603dc1122ae4ce954aadf2eb1943d2` |
| SeestarStudio-2.3.0b2-source.zip | `8b6eea5e7d8d264d869c65fcccd70813d6b436940edd29160dd8612c261abe37` |
| SeestarStudio-2.3.0b2-upstream-sources.zip | `95d2e4764d64d3fbd3cb57d6014273e2aca1aa694a3f2c365e4b81cd09be9101` |

These hashes match the initial GitHub draft asset digests. No existing artifact
was overwritten. A new corrected b3 source kit cannot be accurately labelled or
linked to a binary until the actual b3 source/assets are identified.

## B. Dependencies

The baseline contains 139 native EXE/DLL/PYD files (including the app EXE) and
1,435 embedded PYZ module entries. Installed-package inventories include build
and test tools and are not treated as runtime manifests. Individual RECORD
paths/hashes and exact module names are used for runtime attribution. The
namespace name `PySide6` alone does not prove that WebEngine is shipped.

The full file/native/module mapping is
[B2_BINARY_SOURCE_MAP.json](compliance/B2_BINARY_SOURCE_MAP.json). Fields include
filename, bytes, SHA256, origin/package/version, PE imports including delay imports,
vendor/copyright resources, candidate source/version/URL/hash, license metadata,
modification evidence and outstanding build/source obligations. Unknown entries
remain OPEN. Candidate sources are locally available archives, not proof of what
the older upstream ZIP contained or of a successful native rebuild.

[NATIVE_COMPONENT_REVIEW.md](NATIVE_COMPONENT_REVIEW.md) distinguishes actual
native evidence, static dependencies, OS imports, redistributed Microsoft files,
tools and data. Colorama 0.4.6 was a real omitted runtime notice/source dependency
in the old packaging list; the future list is corrected and the source archive's
PyPI digest verified. 40 source archives and 205 upstream notice files are now
available locally, versus 39/204 in the original baseline package.

## C. Corresponding source and rebuild evidence

The original application source ZIP matches the b2 build metadata source hash
`9668646e07a7a24856d1d536334cbcaa5be73a72fce4489fdf4c27526463a6ed`.
Build/installer scripts, version pins, original app artwork, catalog data and
unmodified SeestarPy source are present. This closes the **application archive
integrity check**, not the complete Corresponding Source requirement.
All 26 vendored SeestarPy Python/web resource files were also compared byte for
byte with its 0.8.0 sdist and matched without changes.

Missing evidence is recorded individually in the native review: Qt/PDF and Mesa
publisher builds; FFmpeg patches/zlib/compiler recipe; CPython native dependencies;
OpenSSL 3.0.16 and 4.0.3; Rust crates/active features; Pillow codec build chain;
OpenBLAS/GCC runtime; astronomy vendored native libraries; installer runtime chain.
Existing native source archives must not be declared sufficient solely because
their version names look right. A Cargo.lock without crate sources or active
feature information is not a complete native source kit.

Existing historical successful application builds use installed wheels. This
audit has not recreated all third-party binaries from source or demonstrated an
independent clean-PC b3 build. Bit-identical output is not imposed as a blanket
license requirement; a documented functionally equivalent rebuild remains the
target. Exact changes to the real b3 source kit and a fresh full EXE/installer
test are pending release identification. The known-good b2 build stays intact.

## D. Licenses and notices

The project is GPL-3.0-only. Original dependency license texts and copyright
notices are retained, including nested duplicate filenames. The license choice
must be assessed per module: Qt Virtual Keyboard is GPLv3, ordinary Qt modules
offer their documented options, FFmpeg's inspected build reports LGPL-2.1-or-later,
Pillow reports MIT-CMU. Do not infer all static codec licenses from Pillow's own.

OpenNGC attribution, snapshot URLs, authors, unchanged data hashes and CC BY-SA 4.0
text are present. The data are kept separate from GPL application code. Changes
to distributed adapted data must be identified and use applicable share-alike
terms. IERS, ERFA/SOFA and astronomy component notices remain separate as well.

The audit includes a real, limited library replacement experiment and instructions
for compatible replacements. Full LGPL/Corresponding Source compliance remains
OPEN/BLOCKER where exact sources/build information are missing. A public Git
repository is not, by itself, proof that every distributed binary has the required
matching source available by the applicable delivery method.

## E. Native components and packaging changes

Exact native hashes/versions and source candidates are recorded, including two
different OpenSSL runtimes, five FFmpeg DLLs, Mesa's embedded version indication,
NumPy's BLAS configuration and Pillow feature versions. MSVC files are classified
separately; no blanket “all DLLs are System Libraries” claim is made.

The local spec removes Qt6Pdf/qpdf, Qt6VirtualKeyboard/its input plugin and five
QML/Quick DLLs. No retained native import references those excluded DLLs. The Qt
probe passed with all normal image plugins and FFmpeg decoding; the loaded changed
QtCore hash was checked through Windows module APIs. Executable code was unchanged
in that library (appended overlay), so this proves acceptance of different DLL
bytes, **not** a rebuilt/custom Qt ABI or every application workflow. Full candidate
regression remains required. See [COMPLIANCE_WORKFLOW.md](COMPLIANCE_WORKFLOW.md).

## F. Security and privacy

The baseline Git scan inspected 348 blobs, 14 trees, one commit and one annotated
tag reachable from local/fetched refs. No key/token pattern or forbidden private
filename was found. Unreachable objects, un-fetched server refs, LFS and files
already sent privately are not silently included in that statement.

Payload checks inspect filenames, raw bytes, decompressed PYZ/CArchive contents
and nested source/base-library ZIPs. No private-key/token match was found. Review
hits comprise upstream Qt build-path strings in byte-identical wheel binaries and
example device IDs in unmodified SeestarPy source/bytecode. These are retained as
review findings, not automatically suppressed or reported as this user's secrets.
Private astronomical coordinates cannot be exhaustively detected by these patterns;
catalog/test reference coordinates are legitimate expected inputs.

The portable archive's 1,423 file contents exactly match the audited onedir.
Historical installer install/reinstall/uninstall evidence reports 1,423 checked
files and zero mismatches; this is reused historical evidence, not a fresh b3
installer extraction or clean external-PC test. No installer was run in this audit.
The installer bootstrap's complete static source/security chain remains OPEN.

181 ignored local JSON/log reports were scanned without displaying matching
contents. They include personal-path/device references and must remain local;
no key/token pattern was found. Personal profiles/authentication directories were
not opened. Private report images and session stores are excluded by packaging
and Git rules, not claimed to have been inspected photograph by photograph.
Actions runs/artifacts were empty in the initial API snapshot. Later remote changes
and the forthcoming b3 assets require a new read-only comparison.

No confirmed secret disclosure incident was found in the inspected public-source
scope. Heuristic scans are not a guarantee of absence. No Git history rewrite,
deletion, release upload or visibility change was performed.

## G. Open legal questions

[ZWO_INTEROPERABILITY_REVIEW.md](ZWO_INTEROPERABILITY_REVIEW.md) describes the actual
local PEM/APK/XAPK processing and challenge-signature mechanism. Entitlement to
process supplied APKs/keys, applicable terms, necessary interoperability steps,
technical protection and trademark questions remain OPEN. The independence notice
is preserved in German and English. No real key value or proprietary APK is in
this report. Relevant statutory provisions are referenced without asserting that
the current workflow automatically meets an exception.

Microsoft redistribution entitlement and individual System Library arguments need
documented review. Codec patents are a separate jurisdiction/use question. No
software-license or packaging test purports to settle those issues.

## H. Publication blockers

| ID | Status | Required evidence/action |
|---|---|---|
| R1 | BLOCKER | Actual b3 URL/assets/source commit and tester-side hashes; do not relabel b2 |
| S1 | BLOCKER | Exact native sources, patches, static dependencies and build recipes for the actual shipped payload |
| F1 | BLOCKER | FFmpeg source/build/patch/zlib correspondence; same-server source delivery check on real release |
| Q1 | BLOCKER | Baseline Qt PDF/Mesa provenance; validate corrected b3 exclusion and full application rebuild |
| N1 | BLOCKER | Other embedded native source/notice gaps and cryptography Rust/OpenSSL chain |
| C1 | BLOCKER for old package | Colorama notice/source omission; local fix must enter a matching corrected package |
| C2 | BLOCKER for old package | Nested vendor license destinations collided; corrected path preservation must enter the matching package |
| M1 | OPEN | Microsoft redistribution entitlement and justified per-component exceptions |
| L1 | OPEN | ZWO interoperability/terms/brands and applicable codec patent review |
| T1 | OPEN | Independent clean-PC source/build/install evidence and complete source-kit reconstruction |
| A1 | OPEN | Final b3 artifact/history/Actions/tester-copy security and integrity comparison |

If the real public b3 package contains these same gaps, recommend a clearly
documented corrected source/notices package and, where needed, a corrected binary
release. If a material unresolved issue requires withdrawing/replacing a download,
present the exact asset/hash and reason for the owner's decision first. No such
action is taken automatically and no legal gap is hidden by deleting its record.

## I. Next actions and evidence locations

1. Obtain the announced b3 link; capture its state and compare every asset hash,
   version and source commit before any correction to release files.
2. Apply the prepared local packaging/notice corrections to the matching source,
   using a separate candidate directory. Run application/UI/decoder tests and
   installer lifecycle tests against that candidate, preserving existing files.
3. Obtain publisher build provenance or create controlled native builds for the
   unresolved source chains; record source hashes, patches, compiler/feature flags
   and enabled static dependencies. Assemble the actual version-specific source kit.
4. Resolve the listed legal issues with appropriate qualified review and the
   project owner. Re-run the nondestructive checker and document any OPEN items.
5. Present exact proposed public changes for explicit approval. Do not publish
   merely because code tests pass or the repository is already public.

Reusable tools: `tools/release_compliance.py`, `tools/qt_compliance_probe.py`,
`tools/qt_packaging.py`. Unit tests cover archive secrecy/path checks, missing or
wrong source hashes, source/build hash ordering/tampering, OPEN status preservation
and Qt dependency rejection. Existing application tests remain part of validation.
The full run passed **166 tests in 22.87 seconds**, followed by a focused run
of the **12 audit/packaging tests**, all passing after the final checker changes. These include
synthetic/offline tests and a local real decoder test, not new telescope tests.

Local raw evidence (ignored by Git): `reports/compliance-2.3.0b3/` contains the
initial GitHub snapshot, machine audit, archive/report scan and Qt probe. Selected
nonsecret evidence is retained under `docs/compliance/` for review. No local
personal logs, key files or telescope images are promoted into documentation.
