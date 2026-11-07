"""Render the original SVG master and an ICO with all Windows icon sizes."""
from pathlib import Path
import io
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from PySide6.QtGui import QImage, QPainter, QGuiApplication
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import Qt, QBuffer, QIODevice
from PIL import Image


def main():
    app = QGuiApplication.instance() or QGuiApplication([])
    root = Path(__file__).resolve().parents[1] / 'seestar_studio/assets'
    renderer = QSvgRenderer(str(root / 'SeestarStudio.svg'))
    assert renderer.isValid()
    image = QImage(1024,1024,QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter=QPainter(image);renderer.render(painter);painter.end()
    buffer=QBuffer();buffer.open(QIODevice.OpenModeFlag.WriteOnly);image.save(buffer,'PNG')
    master=Image.open(io.BytesIO(bytes(buffer.data()))).convert('RGBA')
    master.save(root/'SeestarStudio.png')
    master.save(root/'SeestarStudio.ico',sizes=[(n,n) for n in (16,24,32,48,64,128,256)])
    sizes=Image.open(root/'SeestarStudio.ico').ico.sizes()
    assert sizes=={(n,n) for n in (16,24,32,48,64,128,256)}
    print('Generated original icon:', sorted(sizes))


if __name__=='__main__':main()
