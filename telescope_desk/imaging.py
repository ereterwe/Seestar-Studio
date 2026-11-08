"""SeestarPy decoding/STF; no JPEG re-stretch or browser downsampling."""
import numpy as np
from PySide6.QtGui import QImage


class ImagePipeline:
    def decode(self, header: dict, payload: bytes) -> QImage:
        from seestarpy import stream
        from seestarpy.dashboard.monitor import _block_reduce

        if len(payload) > 256 * 1024 * 1024:
            raise ValueError("Image exceeds size limit")
        arr = stream.decode_payload(payload, header)
        if arr.shape[0] * arr.shape[1] > 40_000_000:
            raise ValueError("Image dimensions exceed limit")
        if arr.ndim == 2:
            # Same Bayer-quad luminance preview as the reference dashboard.
            arr = _block_reduce(arr, 2)
            arr = np.stack([arr, arr, arr], axis=2)
            arr = stream.auto_stretch(arr)
        else:
            arr = stream.to_display8(arr)
        arr = np.ascontiguousarray(arr, dtype=np.uint8)
        h, w = arr.shape[:2]
        return QImage(arr.data, w, h, arr.strides[0], QImage.Format.Format_RGB888).copy()
