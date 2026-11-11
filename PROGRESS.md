# Telescope Desk: current work state

2026-11-11: user requested replacement of the old GitHub version and updated
English information text. Existing remote release is a b2 draft (no public releases).
Prepare current b3 artifacts including corrected notices, push source normally,
replace the obsolete draft only after the new assets are hash-verified. Preserve
Git history and local originals. Public binary promotion remains pending the
documented source/legal checks. Prior no-push restriction is superseded for this update.

2026-11-09 follow-up: Pillow ImageTk/ImageCms/WebP branches excluded and rebuilt.
124 native files (three fewer; 705,536 additional bytes removed). 174 tests pass;
actual packaged Pillow core passes JPEG/PNG/RAW/encoding checks. All native files
are categorized, 105 source archives hash-checked, OpenJPEG supplier patch applies
to its source and is preserved in generated SBOMs. Full static/build correspondence
is still OPEN. See docs/compliance/PILLOW_SOURCE_REVIEW.md and its source map.
New artifacts use separate pillow-review directories; older artifacts remain intact.
Final native portable/installed smoke and install/reinstall/uninstall checks pass.
All 1,670 payload hashes match; existing profiles and previous release artifacts are
unchanged. Local ZIP, installer, SBOM and source candidate are ready for review in
release/pillow-review-2.3.0b3. Evidence: docs/compliance/PILLOW_REVIEW_RESULTS.json.
Native corresponding-source completeness remains a publication BLOCKER, despite
complete source-family assignment. No new hardware test or public upload.

Previous candidate record:

Branch: refactor/telescope-desk-minimal-runtime. Version remains 2.3.0b3.
Baseline preserved at b69a0b28bb78d9b4450d99eb2d5e10e33acfcd59.
Native namespace, executable, UI, installer and developer tools renamed.
Legacy profiles are reused in place; no keys copied. Initial rebuilt payload has
127 native files versus 130, removing Qt Multimedia Widgets and Pillow AVIF.
FFmpeg remains unchanged (183 encoders / 498 decoders).

Completed: 172 tests, final native build, portable/installed clean exit, installer
lifecycle and 1,670-file SBOM coverage. New hardware regression, clean external PC,
software-only graphics and workflow execution remain unverified. Exact embedded
component/source completeness and further FFmpeg minimization remain OPEN.
See docs/compliance/MINIMIZATION_REPORT.md for measurements and release gates.
No main push, merge, public release, binary upload or repository rename.

Current evidence: docs/compliance/MINIMIZATION_REPORT.md. Prior Seestar Studio
records are preserved under docs/history/seestar-studio-b3 and compliance/baseline.
