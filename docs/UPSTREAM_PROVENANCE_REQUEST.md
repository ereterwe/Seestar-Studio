# Prepared upstream technical questions — not sent

These questions can be forwarded to the Qt for Python maintainers after an
explicit instruction to contact them. This audit has not sent email, posted an
issue or shared any user's telescope data. No legal certification is requested.

Subject: Source/build correspondence for official PySide6 6.12.0 Windows x64 wheels

We are preparing a GPL-3.0-only desktop client using the official PySide6 6.12.0,
Essentials, Addons and Shiboken Windows x64 binaries. Publisher-hash-verified
wheels and per-file identities are documented in PUBLISHER_WHEEL_VERIFICATION.json.
Only Widgets/Core/Gui/Network/OpenGL/Svg/Multimedia and relevant plugins are used;
WebEngine, PDF, QML/Quick and Virtual Keyboard are excluded.

1. Please identify source revisions, any additional patches and effective build
   options for these wheel libraries/plugins, or confirm their relation to the
   public 6.12.0 source archives and build scripts. Generic source availability
   and DLL version strings do not identify every original build input.
2. For FFmpeg, we found the 6.12.0 coin Windows provisioning recipe, the matching
   FFmpeg 9.0.1 source archive/checksum and the zlib 1.3.1 recipe including its two
   Windows edits. Exported FFmpeg configuration matches these principal inputs.
   Please confirm the corresponding wheel build and any additional build/patch
   information needed for compatible modified libraries.
3. For opengl32sw.dll we verified the Mesa 11.2.2 signed_sha256 archive named in
   coin. Its PE sections match the wheel DLL, while complete files differ. The
   implementation indicates LLVM 3.6.2. Can you identify the actual Mesa/LLVM
   source revisions, Windows patches and producing build instructions for this
   renderer, including retained copyright notices for static parts?
4. Are there release-specific records for embedded third-party versions/features
   that supplement the collected module attribution manifests and source archives?

We do not require bit-identical output, a particular SBOM format or a legal opinion.
The goal is complete corresponding source and compatible modification/rebuild
instructions. All proposed attachments contain public package metadata/hashes
only, not project binaries, keys, APKs or user observing information.
