from PyQt5.Qt import *
from PyQt5.QtCore import *
import math


class Scene(QGraphicsScene):

    cur_shape = None
    clip_area = None
    border_color = Qt.black
    fill_color = Qt.NoBrush
    pen_width = 2
    pen_style = Qt.SolidLine
    cap_style = Qt.SquareCap
    join_style = Qt.BevelJoin
    release = True

    def __init__(self, parent=None):
        super().__init__(parent)

    def set_cur_shape(self, shape):
        self.cur_shape = shape
        if self.clip_area is not None:
            self.removeItem(self.clip_area)
            self.clip_area = None

    def set_clip_area(self, shape):
        self.clip_area = shape

    def clip(self):
        if self.clip_area:
            for it in self.items():
                if not self.clip_area.contains(it.boundingRect().topLeft()) \
                        and not self.clip_area.contains(it.boundingRect().topRight()) \
                        and not self.clip_area.contains(it.boundingRect().bottomLeft()) \
                        and not self.clip_area.contains(it.boundingRect().bottomRight()):
                    self.removeItem(it)
            self.clip_area = None

    def rotate(self):
        sender = self.sender()
        for it in self.selectedItems():
            # it.setTransformOriginPoint(it.boundingRect().center())
            if sender.objectName() == "actionRotate_To_Left":
                it.setTransformOriginPoint(it.boundingRect().center())
                it.angle = it.angle - 90
                it.setRotation(it.angle)
            elif sender.objectName() == "actionRotate_To_Right":
                it.setTransformOriginPoint(it.boundingRect().center())
                it.angle = it.angle + 90
                it.setRotation(it.angle)
            elif sender.objectName() == "actionFlip_Horizontal":
                it.setTransformOriginPoint(it.boundingRect().center())
                transform = it.transform()
                transform.translate(it.boundingRect().center().x(), it.boundingRect().center().y())
                transform.rotate(180, Qt.YAxis)
                transform.translate(-it.boundingRect().center().x(), -it.boundingRect().center().y())
                it.setTransform(transform)
            elif sender.objectName() == "actionFlip_Vertical":
                it.setTransformOriginPoint(it.boundingRect().center())
                transform = it.transform()
                transform.translate(it.boundingRect().center().x(), it.boundingRect().center().y())
                transform.rotate(180, Qt.XAxis)
                transform.translate(-it.boundingRect().center().x(), -it.boundingRect().center().y())
                it.setTransform(transform)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if not event.isAccepted() and event.button() == Qt.LeftButton:
            if self.cur_shape:
                self.release = False
                self.cur_shape.set_border_color(self.border_color)
                self.cur_shape.set_fill_color(QBrush(self.fill_color))
                self.cur_shape.set_pen_width(self.pen_width)
                self.cur_shape.set_pen_style(self.pen_style)
                self.cur_shape.set_cap_style(self.cap_style)
                self.cur_shape.set_join_style(self.join_style)
                self.cur_shape.start_draw(event)
                self.addItem(self.cur_shape)
            elif self.clip_area:
                self.release = False
                self.clip_area.set_border_color(Qt.black)
                self.clip_area.set_fill_color(QBrush(Qt.NoBrush))
                self.clip_area.set_pen_width(1.0)
                self.clip_area.set_pen_style(Qt.DotLine)
                self.clip_area.start_draw(event)
                if self.clip_area not in self.items():
                    self.addItem(self.clip_area)
        elif not event.isAccepted() and event.button() == Qt.RightButton:
            item_to_remove = None
            for it in self.items(event.scenePos()):
                if it.type() == QGraphicsItem.UserType + 1:
                    item_to_remove = it
                    break
            if item_to_remove:
                self.removeItem(item_to_remove)

    def mouseMoveEvent(self, event):
        if self.cur_shape and not self.release:
            self.cur_shape.drawing(event)
        elif self.clip_area and not self.release:
            self.clip_area.drawing(event)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.release = True
        self.cur_shape = None
        if self.clip_area and math.sqrt(math.pow(self.clip_area.boundingRect().topLeft().x() -
                                                 self.clip_area.boundingRect().bottomRight().x(), 2) +
                                        math.pow(self.clip_area.boundingRect().topLeft().y() -
                                                 self.clip_area.boundingRect().bottomRight().y(), 2)) <= 6:
            self.removeItem(self.clip_area)
            self.clip_area = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace:
            while self.selectedItems():
                self.removeItem(self.selectedItems()[0])
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.clip()
        else:
            super().keyPressEvent(event)
