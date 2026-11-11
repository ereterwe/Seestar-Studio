# Telescope Desk: current work state

2026-11-11: source/draft replacement completed. GitHub main and English information
text updated; obsolete b2 draft deleted; all six b3 assets uploaded/hash-verified.
See docs/compliance/GITHUB_UPDATE_2026-11-11.json. Next: resolve the outstanding
native source and legal gates before public binary promotion, and perform new
hardware/external-PC regression tests. The replacement remains a draft.

2026-11-09: Pillow branch pruning and native source-candidate assignment completed;
see docs/compliance/PILLOW_SOURCE_REVIEW.md. Next unresolved technical work:
exact remaining static-component/build provenance (especially Qt/Mesa), then a
compatible FFmpeg reduction with actual RTSP/Live View regression evidence.
Custom Pillow core removal of TIFF/OpenJPEG would require its own verified build.
New candidate still needs real-hardware and external clean-PC regression tests.
No public release until remaining release gates and explicit authorization.

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
