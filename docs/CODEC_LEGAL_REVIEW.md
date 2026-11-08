# Codecs: facts and questions for legal review

Deutsche Kurzfassung: Das Paket enthält H.264, HEVC, AV1 und AAC, auch wenn die
Anwendung keine Video-/Audioaufnahme startet. Der veröffentlichte AVC-PC-Tarif
beginnt mit 0 USD für die ersten 100.000 Einheiten; daraus folgt keine automatische
Vertrags- oder Meldefreiheit. Bei HEVC ist kostenlose Software nicht allgemein
ausgenommen. AV1s AOM-Lizenz betrifft ihren definierten Rechteumfang. Profile,
Länder und Vertriebsmodell müssen bewertet werden. OBS-Streaming ist eine
getrennte Nutzerfunktion. Nachfolgend stehen Belege, Bedingungen und konkrete Fragen.

Status: evidence dossier, not a patent licence or legal clearance. Checked
8 November 2026. Candidate: local Seestar Studio 2.3.0b3. Registry evidence is
`docs/compliance/CODEC_REGISTRY.json`; the DLL hash binds it to the candidate.

## Product and actual behaviour

Seestar Studio is a free GPL Windows desktop application. It receives local LAN
telescope images and RTSP video. `video.py` uses QMediaPlayer/QVideoSink; no video
encoder or audio recorder is invoked by this implementation. No videos are
uploaded, hosted, sold or transmitted to an Internet audience by the application.
Users may capture the window with their separate OBS installation. OBS/service
licensing and content distribution are separate from our decoder distribution.

The current FFmpeg 9.0.1 binary registry contains **498 decoders and 183 encoders**.
Compiled capability is broader than application use. Registered families include
H.264/AVC, HEVC/H.265, AV1, VP9, AAC and MJPEG, with some Windows hardware/Media
Foundation variants. This count is per registered implementation, not per standard.
It does not prove that each codec has successfully decoded a real telescope stream.
Actual codecs/profiles emitted by every supported firmware remain unverified.

Pillow adds an independent AVIF path: the installed matching `_avif` extension
reports **dav1d 1.5.3** decoding and **libaom 3.14.1** encoding. Rav1e, SVT and
libgav1 are not enabled there. Library encoding capability must be disclosed even
though the application does not intentionally export AVIF. Basic JPEG/PNG/raw
stack viewers are distinct from H.264 video. The Pillow publisher's generic SBOM
also lists optional components: it is not evidence that every item is enabled.
For example libimagequant is disabled in the examined extension; the FreeType
extension is not part of the b3 payload.

## Copyright licences versus patents

The five FFmpeg DLLs report LGPL-2.1-or-later. Their configuration contains no
`--enable-gpl` or `--enable-nonfree`. Exact source, build, static dependency,
notice and replacement obligations still need their own evidence. A successful
copyright licence check does not grant independent patent rights.
[FFmpeg's own legal page](https://ffmpeg.org/legal.html) treats both topics and
requires matching source/build material in its recommended compliance route.

## H.264 / AVC

[Via LA's AVC programme](https://www.via-la.com/licensing-programs/avc-h-264/)
expressly covers PC software encoders/decoders. Its published PC-product schedule
shows USD 0 for the first 100,000 units per year, then USD 0.20 up to five million
and USD 0.10 above that, subject to programme definitions/grouping and a cap.
This is a tariff summary, not confirmation that our product owes those amounts
or needs no agreement below the threshold. The actual licence controls. Determine
our contracting entity, territory, relevant units, reporting and end-user scope.
Do not apply the separate Internet content-streaming tariffs to this LAN viewer
without establishing why that category applies.

## HEVC / H.265

[Access Advance's FAQ](https://accessadvance.com/faq/) says free downloaded HEVC
software generally requires a licence, with case-specific situations where it
does not. It ties royalty analysis to relevant patents/territories and directs
software providers to clarify their circumstances. This is a pool administrator's
position, not a court finding about Seestar Studio. HEVC also has a separate
[VCL Advance programme](https://www.via-la.com/licensing-programs/hevc-vvc/).
Review applicable portfolios/exceptions, existing device/platform coverage and
residual non-pool rights; one agreement must not be assumed to clear every claim.

## AV1 / VP9 and still-image AVIF

[AOMedia](https://aomedia.org/about/story/) describes its royalty-free AV1 policy.
The [AOM Patent License 1.0](https://aomedia.org/license/patent/) grants rights
within its defined contributor/necessary-claim scope and includes termination
conditions. It does not establish that every third-party claimant is covered.
Record both FFmpeg's registered AV1/VP9 capability and Pillow's AVIF/AOM/dav1d path.
Ask whether any proposed pool programme actually applies to our desktop decoder
distribution; its name or inclusion of AV1 in an Internet-video pool is not enough.

## AAC and other bundled codecs

[Via LA's AAC programme](https://www.via-la.com/licensing-programs/aac/) covers
multiple AAC-family profiles; published terms/rates cannot be applied to this
product without determining the relevant implementation, use and exemptions.
The app currently has no audio feature, but the generic FFmpeg binaries expose
AAC. Do not infer that every AAC profile or patent has expired. The complete
registry is available for a broader assessment of legacy/MPEG and image formats.

## Facts the reviewer must decide, not assumptions

1. Publisher/legal entity and release countries; worldwide GitHub availability
   is the present distribution proposal, not a completed territory assessment.
2. Completely free distribution versus any later paid features, donations or
   commercial support; no such future arrangement is established here.
3. Counting licensed units and affiliated entities, applicable agreements,
   registration/reporting duties even where a royalty threshold is zero.
4. Whether existing Windows/GPU/device licences cover anything relevant, for
   whom, and whether they cover distribution of our separate software decoder.
5. Which real device codecs/profiles are essential versus merely bundled; source
   inspection/registry enumeration is not a hardware compatibility test.
6. Patent validity, essentiality, remaining term and territorial reach. A pool
   tariff is not proof that a particular asserted patent is infringed.

No request was sent to a pool or rights holder and no contract was accepted.

## Technical ways to reduce the question

An independently built FFmpeg can omit unused encoders/audio/extra decoders and
retain only verified stream formats plus test formats. This reduces bundled
capability but does not itself clear necessary H.264/HEVC patents. A Windows-native
backend changes the component source; it is not an automatic patent exemption.
A stack-image-only variant could omit RTSP video, with a clearly documented loss
of live-video functionality. No such reduction is applied silently to b3.
