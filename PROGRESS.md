# Telescope Desk: current work state

Branch: refactor/telescope-desk-minimal-runtime. Version remains 2.3.0b3.
Baseline preserved at b69a0b28bb78d9b4450d99eb2d5e10e33acfcd59.
Native namespace, executable, UI, installer and developer tools renamed.
Legacy profiles are reused in place; no keys copied. Initial rebuilt payload has
127 native files versus 130, removing Qt Multimedia Widgets and Pillow AVIF.
FFmpeg remains unchanged (183 encoders / 498 decoders).

Remaining validation: final clean build tied to a local commit, native UI/installer
lifecycle and payload/SBOM checks. Renewed real-device Live View, clean external
Windows and software-only graphics tests remain unverified. Complete embedded
static-component SBOM/source reconstruction and legal decisions remain OPEN.
No main push, merge, public release, binary upload or repository rename.

Current evidence: docs/compliance/MINIMIZATION_REPORT.md. Prior Seestar Studio
records are preserved under docs/history/seestar-studio-b3 and compliance/baseline.
