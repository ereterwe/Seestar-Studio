# Telescope Desk Windows build

Use Python 3.12 x64 and requirements-lock.txt in .venv. Run build.ps1, then
build-installer.ps1 (Inno Setup 7.1.1). Outputs are dist/2.3.0b3/TelescopeDesk and
release/TelescopeDesk-2.3.0b3-*. Existing Seestar Studio outputs are separate.
Version is unchanged. Build metadata records source hash and Git commit/dirty state.

For an isolated candidate use PyInstaller --clean --distpath dist/telescope-desk-2.3.0b3
--workpath build/telescope-desk-2.3.0b3 TelescopeDesk.spec after tools.build_metadata.
Then tools.license_audit, tools.package_release and build-installer.ps1 accept explicit
target/output paths. See their --help/PowerShell parameters. Keep full onedir folders;
Qt libraries remain dynamically replaceable.

Use tools.release_compliance on the selected payload, then tools.runtime_sbom to
produce a file-complete CycloneDX inventory. Embedded static completeness remains
explicitly OPEN. tools.source_candidate assembles known original sources plus the
matching application source ZIP; it refuses overwrites and checks archive hashes.
It needs the local third_party_sources cache from docs/DEPENDENCY_SOURCES.json.
Its corresponding-source filename does not certify legal completeness.

The manual Windows workflow requires a trusted self-hosted Windows x64 runner with
Python 3.12, Inno 7.1.1 and the verified upstream source cache. It builds/tests locally
on the runner; no upload/release step or write permission exists. Workflow execution
has not been verified on GitHub. Never run untrusted PR code on that runner.

The DLL replacement probe changes an overlay of a copied Qt DLL; it establishes
loading of different bytes, not a custom rebuilt Qt ABI. Clean external Windows,
software-rendering-only hosts and renewed hardware regression remain pending.
Native source and legal limitations: docs/compliance/MINIMIZATION_REPORT.md.
Historical exact build guidance: docs/history/seestar-studio-b3/BUILDING.md.
