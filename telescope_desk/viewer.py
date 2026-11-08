from .i18n import source as ui_text, tr
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

class ImageViewer(QGraphicsView):
    maximize_requested = Signal()
    zoom_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))
        self.item = QGraphicsPixmapItem()
        self.scene().addItem(self.item)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(Qt.GlobalColor.black)
        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.fit_mode = True
        self.setMinimumHeight(160)
        self.setToolTip(ui_text('m0255'))

    def set_image(self, image):
        old_size = self.item.pixmap().size()
        center = self.mapToScene(self.viewport().rect().center())
        self.item.setPixmap(QPixmap.fromImage(image))
        self.scene().setSceneRect(self.item.boundingRect())
        if self.fit_mode or old_size.isEmpty():
            self.fit_image()
        elif old_size != image.size():
            self.centerOn(center.x() * image.width() / old_size.width(), center.y() * image.height() / old_size.height())
        else:
            self.centerOn(center)

    def fit_image(self):
        self.fit_mode = True
        if not self.item.pixmap().isNull():
            self.fitInView(self.item, Qt.AspectRatioMode.KeepAspectRatio)
        self.zoom_changed.emit(ui_text('m0008'))

    def actual_size(self):
        self.fit_mode = False
        self.resetTransform()
        self.zoom_changed.emit('100 %')

    def wheelEvent(self, event):
        if self.item.pixmap().isNull():
            return
        self.fit_mode = False
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        scale = self.transform().m11() * factor
        if 0.02 <= scale <= 16:
            self.scale(factor, factor)
        self.zoom_changed.emit(f'{self.transform().m11() * 100:.0f} %')
        event.accept()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.fit_mode:
            self.fit_image()

    def mouseDoubleClickEvent(self, event):
        self.maximize_requested.emit()
        event.accept()
