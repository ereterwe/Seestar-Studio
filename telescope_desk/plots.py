"""Small dependency-free Qt plots; values stay local."""
from .i18n import source as ui_text, tr
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QPainterPath
from PySide6.QtWidgets import QWidget

class LinePlot(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(180)
        self.series = []
        self.labels = ('', '')
        self.bounds = (-30, 90)

    def set_series(self, series, labels=('', ''), bounds=(-30, 90)):
        self.series, self.labels, self.bounds = (series, labels, bounds)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(42, 15, max(1, self.width() - 60), max(1, self.height() - 45))
        low, high = self.bounds
        for value in (low, (low + high) / 2, high):
            y = r.bottom() - (value - low) / max(high - low, 1) * r.height()
            p.setPen(QPen(QColor('#303842'), 1))
            p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
            p.setPen(QColor('#9aa7b4'))
            p.drawText(QRectF(0, y - 9, 36, 20), Qt.AlignmentFlag.AlignRight, tr(f'{value:g}'))
        for series in self.series:
            values, color = series[:2]
            positions = series[2] if len(series) > 2 else None
            if len(values) < 2:
                continue
            path = QPainterPath()
            active = False
            for i, value in enumerate(values):
                if value is None:
                    active = False
                    continue
                fraction = positions[i] if positions is not None else i / (len(values) - 1)
                point = QPointF(r.left() + fraction * r.width(), r.bottom() - (max(low, min(high, value)) - low) / max(high - low, 1) * r.height())
                if active:
                    path.lineTo(point)
                else:
                    path.moveTo(point)
                    active = True
            p.setPen(QPen(QColor(color), 2))
            p.drawPath(path)
        p.setPen(QColor('#9aa7b4'))
        p.drawText(QRectF(r.left(), r.bottom() + 5, r.width(), 24), Qt.AlignmentFlag.AlignLeft, tr(self.labels[0]))
        p.drawText(QRectF(r.left(), r.bottom() + 5, r.width(), 24), Qt.AlignmentFlag.AlignRight, tr(self.labels[1]))
