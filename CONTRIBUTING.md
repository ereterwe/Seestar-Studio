# Contributing to Telescope Desk

Own code is GPL-3.0-only. Preserve upstream names, copyright and license texts.
Use Python 3.12, the locked dependencies and pytest. App namespace: telescope_desk.
Build with build.ps1 and build-installer.ps1; see BUILDING.md for prerequisites.

Use feature branches. Current cleanup branch: refactor/telescope-desk-minimal-runtime.
No push/merge to main, repository rename or public binary upload is authorized by
the cleanup task. Manual CI has no upload/release step.

Never commit user keys, APKs, locations, telescope identities, session databases,
photos or logs. Unit tests isolate discovery. Real movement/capture commands need
explicit permission. Label simulations separately from hardware evidence.

Retain unknown dynamic/firmware/graphics dependencies until removal is justified.
Update actual payload inventory, SBOM, corresponding-source evidence and notices
when changing runtime packaging. File coverage is not complete static-link provenance
or legal clearance. See docs/compliance/MINIMIZATION_REPORT.md.
