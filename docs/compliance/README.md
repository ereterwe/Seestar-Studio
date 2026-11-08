# Compliance evidence for local 2.3.0b3

B3 is newly built from the b2 baseline after the owner's clarification. B2-prefixed
files retain the earlier immutable comparison evidence. B3_BINARY_SOURCE_MAP.json
contains the new complete payload/native/PYZ mapping; AUDIT_CHECKS.json contains
its PASS/OPEN/BLOCKER results, and B3_SMOKE_TEST.json contains nonpersonal native
EXE smoke results. Raw device data, screenshots and credentials are excluded.
166 automated tests passed. Native source/build and legal gaps remain documented.

## Earlier baseline evidence


All evidence concerns the **local b2 baseline** unless explicitly stated otherwise.
B3 is now built locally. No legal clearance or hardware
test is claimed. The source repository is public; the refreshed API still shows
the same b2 draft and asset hashes.

| File | What it establishes |
|---|---|
| RELEASE_STATE.json | Minimal timestamped GitHub state, release assets and hashes; no credentials or user-profile dump |
| B2_BINARY_SOURCE_MAP.json | Complete payload/native/PYZ inventories, local origins, source candidates and explicit unknowns |
| AUDIT_CHECKS.json | PASS/OPEN/BLOCKER checks on the baseline; 166 automated tests passed for b3 |
| NATIVE_RUNTIME_EVIDENCE.json | FFmpeg exports, Pillow/NumPy/OpenSSL/SQLite/WCSLIB facts, bounded Mesa version indication |
| CRYPTOGRAPHY_RUST_LOCK.json | Source lockfile candidates; active linkage and delivered crate sources not proved |
| QT_PAYLOAD_PROBE.json | Isolated changed-DLL loading, widget/image/decoder test and exact excluded files |
| NOTICE_COLLISION_EVIDENCE.json | Two original setuptools notice-path collisions; corrected destinations do not collide |
| SEESTARPY_SOURCE_COMPARISON.json | 26 vendored source/resource files exactly match the 0.8.0 sdist |

Full private work logs remain under ignored `reports/`. Hashes and original
dependency notices are evidence, not consent to republish personal logs. The
baseline's historical `repository_visibility: private` field is its build-time
metadata, not the current repository state. Machine source candidates reference
the local source archive inventory; they do not retroactively amend old ZIPs.

B3_INSTALLER_TEST.json records the final local installer lifecycle; B3_ARTIFACTS.json
records the four immutable local candidate archives/installer. Final audit exports
are kept outside the payload to avoid recursive self-hashing.
