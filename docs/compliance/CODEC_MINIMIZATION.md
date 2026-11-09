# Codec minimization — Telescope Desk 2.3.0b3

Baseline FFmpeg: 498 decoder and 183 encoder implementations, not distinct standards.
The original FFmpeg DLLs are retained byte-for-byte, so these counts are unchanged.
RTSP DESCRIBE/SETUP/PLAY, RTP transport, parsers/demuxers, hardware and software
fallbacks must remain available. The developer confirmed working real Live View;
its model/firmware/emitted codec is not sufficiently specified. A port-open or GIF
playback test does not establish every RTSP/codec variant.

The app uses QMediaPlayer -> QVideoSink -> QVideoFrame.toImage -> latest-frame
mailbox -> Qt image viewer. No QVideoWidget, QGraphicsVideoItem or recorder is used.
PyInstaller's QtMultimedia hook adds QtMultimediaWidgets unconditionally; the spec
excludes that Python module and a PE import/delay-import guard excludes its DLL.

JPEG/raw stacks come from SeestarPy. Thumbnail allowlist is jpg/jpeg/png;
image export uses Qt. Exclude PIL.AvifImagePlugin and PIL._avif at module analysis,
removing the independent AVIF/libaom/dav1d encoder/decoder branch from Pillow.
This does not remove FFmpeg AV1. The subsequent Pillow review also removes its
Tk/CMS/WebP branches (PILLOW_SOURCE_REVIEW.md). Qt image codecs and the remaining
Pillow core static codecs stay retained pending separate build/link validation.

A smaller FFmpeg requires a compatible shared build and Qt integration testing;
removing exported encode APIs can break Qt even if the app never records. Do not
replace the proven build without a transport/codec regression matrix. Unused
FFmpeg encoders remain a documented minimization opportunity, not an achieved removal.

Windows Media Foundation is an alternative backend, not proven equivalent for
these RTSP streams and Windows variants. No switch is made. OS codecs do not imply
patent clearance. Original Qt guidance: https://doc.qt.io/qt-6/qtmultimedia-index.html
and https://doc.qt.io/qt-6/qtmultimedia-building-ffmpeg-windows.html.

New reference-stream, payload and hardware results are recorded in MINIMIZATION_REPORT.md.
Patent questions for AVC/HEVC/AV1/VP9/AAC remain, including compiled unused capability.
