from PyQt5.Qt import *
import math

STRETCH_RECT_WIDTH = 3.0
STRETCH_RECT_HEIGHT = 3.0


def distance(p1, p2):
    if math.sqrt(math.pow(p1.x() - p2.x(), 2) + math.pow(p1.y() - p2.y(), 2)) < 3:
        return True
    else:
        return False


def get_rotation_angle(origin, start, end):
    origin_to_start = math.sqrt(math.pow(origin.x() - start.x(), 2) + math.pow(origin.y() - start.y(), 2))
    origin_to_end = math.sqrt(math.pow(origin.x() - end.x(), 2) + math.pow(origin.y() - end.y(), 2))
    start_to_end = math.sqrt(math.pow(start.x() - end.x(), 2) + math.pow(start.y() - end.y(), 2))
    if origin_to_start == 0 or origin_to_end == 0:
        print("fuck")
    angle = math.acos((math.pow(origin_to_start, 2) + math.pow(origin_to_end, 2) - math.pow(start_to_end, 2))
                      / (2 * origin_to_start * origin_to_end)) * 180 / math.pi
    if start.x() <= end.x():
        print(angle)
        return angle
    else:
        print(-angle)
        return -angle


class Line(QGraphicsLineItem):

    center_point = None
    resize = ""
    rotate = False
    angle = 0
    last_x = 0
    last_y = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

    def start_draw(self, event):
        self.setCursor(Qt.CrossCursor)
        self.setLine(QLineF(self.mapFromScene(event.scenePos()), self.mapFromScene(event.scenePos())))

    def drawing(self, event):
        self.setLine(QLineF(self.line().p1(), self.mapFromScene(event.scenePos())))

    def mousePressEvent(self, event):

        p1 = self.line().p1()
        p2 = self.line().p2()
        self.center_point = (p1 + p2) / 2
        cur_pos = self.mapFromScene(event.scenePos())

        if event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.ShiftModifier:  # 左键+shift：选中
                self.setSelected(True)
            elif distance(cur_pos, p1) or distance(cur_pos, p2):
                self.setFlag(QGraphicsItem.ItemIsMovable, False)
                self.setCursor(Qt.SizeAllCursor)
                if distance(cur_pos, p1):
                    self.resize = "p1"
                elif distance(cur_pos, p2):
                    self.resize = "p2"
                self.last_x = cur_pos.x()
                self.last_y = cur_pos.y()
            else:
                super().mousePressEvent(event)
                event.accept()
        elif event.button() == Qt.RightButton:
            event.ignore()

    def mouseMoveEvent(self, event):
        if self.resize:
            self.prepareGeometryChange()
            p1 = self.line().p1()
            p2 = self.line().p2()
            cur_pos = self.mapFromScene(event.scenePos())

            if self.resize == "p1":
                self.setLine(cur_pos.x(), cur_pos.y(), p2.x(), p2.y())
            elif self.resize == "p2":
                self.setLine(p1.x(), p1.y(), cur_pos.x(), cur_pos.y())

            self.center_point = (self.line().p1() + self.line().p2()) / 2
            self.last_x = cur_pos.x()
            self.last_y = cur_pos.y()

        elif event.modifiers != Qt.AltModifier:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.resize:
            self.resize = ""
            self.last_x = 0
            self.last_y = 0
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
        else:
            super().mouseReleaseEvent(event)
        self.setCursor(Qt.ArrowCursor)

    def paint(self, painter, option, widget=None):
        op = QStyleOptionGraphicsItem()
        if widget:
            op.initFrom(widget)
        if option.state & QStyle.State_Selected:
            op.state = QStyle.State_None
        super().paint(painter, op, widget)
        if option.state & QStyle.State_Selected:
            p1 = self.line().p1()
            p2 = self.line().p2()
            painter.setPen(Qt.white)
            painter.setBrush(QColor(0, 174, 255))
            painter.drawEllipse(p1, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)
            painter.drawEllipse(p2, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)
            painter.drawEllipse(self.center_point, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)

    def type(self):
        return self.UserType + 1

    def set_border_color(self, color):
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def set_fill_color(self, color):
        pass

    def set_pen_width(self, pen_width):
        pen = self.pen()
        pen.setWidth(pen_width)
        self.setPen(pen)

    def set_pen_style(self, pen_style):
        pen = self.pen()
        pen.setStyle(pen_style)
        self.setPen(pen)

    def set_cap_style(self, cap_style):
        pen = self.pen()
        pen.setCapStyle(cap_style)
        self.setPen(pen)

    def set_join_style(self, join_style):
        pen = self.pen()
        pen.setJoinStyle(join_style)
        self.setPen(pen)


class Rectangle(QGraphicsRectItem):

    center_point = None
    resize = ""
    rotate = False
    angle = 0
    last_x = 0
    last_y = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)

    def start_draw(self, event):
        self.setCursor(Qt.CrossCursor)
        self.setRect(QRectF(self.mapFromScene(event.scenePos()), QSizeF(0, 0)))

    def drawing(self, event):
        self.setRect(QRectF(self.rect().topLeft(),
                            QSizeF(abs(event.scenePos().x() - self.mapToScene(self.rect().topLeft()).x()),
                            abs(event.scenePos().y() - self.mapToScene(self.rect().topLeft()).y()))))

    def mousePressEvent(self, event):

        top_left = self.rect().topLeft()
        top_right = self.rect().topRight()
        bottom_left = self.rect().bottomLeft()
        bottom_right = self.rect().bottomRight()
        left_center = QPointF(top_left.x(), (top_left.y() + bottom_left.y()) / 2)
        right_center = QPointF(top_right.x(), left_center.y())
        top_center = QPointF((top_left.x() + top_right.x()) / 2, top_left.y())
        bottom_center = QPointF(top_center.x(), bottom_left.y())
        origin = QPointF(top_center.x(), left_center.y())
        cur_pos = self.mapFromScene(event.scenePos())

        if event.button() == Qt.LeftButton:
            if event.modifiers() == Qt.ShiftModifier:  # 左键+shift：选中
                self.setSelected(True)
            elif distance(cur_pos, top_left) or distance(cur_pos, top_right) \
                    or distance(cur_pos, bottom_left) or distance(cur_pos, bottom_right) \
                    or distance(cur_pos, left_center) or distance(cur_pos, right_center) \
                    or distance(cur_pos, top_center) or distance(cur_pos, bottom_center) \
                    or distance(cur_pos, origin):
                self.setFlag(QGraphicsItem.ItemIsMovable, False)
                if distance(cur_pos, top_left):
                    self.setCursor(Qt.SizeFDiagCursor)
                    self.resize = "top_left"
                elif distance(cur_pos, top_right):
                    self.setCursor(Qt.SizeBDiagCursor)
                    self.resize = "top_right"
                elif distance(cur_pos, bottom_left):
                    self.setCursor(Qt.SizeBDiagCursor)
                    self.resize = "bottom_left"
                elif distance(cur_pos, bottom_right):
                    self.setCursor(Qt.SizeFDiagCursor)
                    self.resize = "bottom_right"
                elif distance(cur_pos, left_center):
                    self.setCursor(Qt.SizeHorCursor)
                    self.resize = "left_center"
                elif distance(cur_pos, right_center):
                    self.setCursor(Qt.SizeHorCursor)
                    self.resize = "right_center"
                elif distance(cur_pos, top_center):
                    self.setCursor(Qt.SizeVerCursor)
                    self.resize = "top_center"
                elif distance(cur_pos, bottom_center):
                    self.setCursor(Qt.SizeVerCursor)
                    self.resize = "bottom_center"
                # elif distance(cur_pos, origin):
                    # self.setCursor(Qt.ClosedHandCursor)
                    # self.rotate = True
                self.last_x = cur_pos.x()
                self.last_y = cur_pos.y()
                width_radius = self.rect().width() / 2.0
                height_radius = self.rect().height() / 2.0
                self.center_point = QPointF(top_left.x() + self.pos().x() + width_radius,
                                            top_left.y() + self.pos().y() + height_radius)
            else:
                super().mousePressEvent(event)
                event.accept()
        elif event.button() == Qt.RightButton:
            event.ignore()

    def mouseMoveEvent(self, event):
        cur_pos = self.mapFromScene(event.scenePos())
        top_left = self.rect().topLeft()
        top_right = self.rect().topRight()
        bottom_left = self.rect().bottomLeft()
        bottom_right = self.rect().bottomRight()
        left_center = QPointF(top_left.x(), (top_left.y() + bottom_left.y()) / 2)
        right_center = QPointF(top_right.x(), left_center.y())
        top_center = QPointF((top_left.x() + top_right.x()) / 2, top_left.y())
        bottom_center = QPointF(top_center.x(), bottom_left.y())
        # origin = QPointF(top_center.x(), left_center.y())

        if self.resize:
            if self.resize == "top_left":
                self.setRect(cur_pos.x(), cur_pos.y(), bottom_right.x() - cur_pos.x(), bottom_right.y() - cur_pos.y())
            elif self.resize == "top_right":
                self.setRect(bottom_left.x(), cur_pos.y(), cur_pos.x() - bottom_left.x(), bottom_left.y() - cur_pos.y())
            elif self.resize == "bottom_left":
                self.setRect(cur_pos.x(), top_right.y(), top_right.x() - cur_pos.x(), cur_pos.y() - top_right.y())
            elif self.resize == "bottom_right":
                self.setRect(top_left.x(), top_left.y(), cur_pos.x() - top_left.x(), cur_pos.y() - top_left.y())
            elif self.resize == "left_center":
                self.setRect(cur_pos.x(), top_left.y(), top_right.x() - cur_pos.x(), bottom_left.y() - top_left.y())
            elif self.resize == "right_center":
                self.setRect(top_left.x(), top_left.y(), cur_pos.x() - top_left.x(), bottom_left.y() - top_left.y())
            elif self.resize == "top_center":
                self.setRect(top_left.x(), cur_pos.y(), top_right.x() - top_left.x(), bottom_left.y() - cur_pos.y())
            elif self.resize == "bottom_center":
                self.setRect(top_left.x(), top_left.y(), top_right.x() - top_left.x(), cur_pos.y() - top_left.y())

        # elif self.rotate:
            # self.angle = get_rotation_angle(origin, QPointF(self.last_x, self.last_y), cur_pos)
            # self.setRotation(self.angle)
        else:
            super().mouseMoveEvent(event)

        self.setTransformOriginPoint(self.rect().center())
        self.last_x = cur_pos.x()
        self.last_y = cur_pos.y()

    def mouseReleaseEvent(self, event):
        if self.resize or self.rotate:
            self.resize = ""
            self.rotate = False
            self.last_x = 0
            self.last_y = 0
            self.setFlag(QGraphicsItem.ItemIsMovable, True)
        else:
            super().mouseReleaseEvent(event)
        self.setCursor(Qt.ArrowCursor)

    def paint(self, painter, option, widget=None):
        op = QStyleOptionGraphicsItem()
        if widget:
            op.initFrom(widget)
        if option.state & QStyle.State_Selected:
            op.state = QStyle.State_None
        super().paint(painter, op, widget)
        if self.scene().clip_area == self or option.state & QStyle.State_Selected:
            top_left = self.rect().topLeft()
            top_right = self.rect().topRight()
            bottom_left = self.rect().bottomLeft()
            bottom_right = self.rect().bottomRight()
            left_center = QPointF(top_left.x(), (top_left.y() + bottom_left.y()) / 2)
            right_center = QPointF(top_right.x(), left_center.y())
            top_center = QPointF((top_left.x() + top_right.x()) / 2, top_left.y())
            bottom_center = QPointF(top_center.x(), bottom_left.y())
            # origin = QPointF(top_center.x(), left_center.y())
            painter.setPen(Qt.white)
            painter.setBrush(QColor(0, 174, 255))
            painter.drawEllipse(top_left, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)
            painter.drawEllipse(top_right, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)
            painter.drawEllipse(bottom_left, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)
            painter.drawEllipse(bottom_right, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)
            painter.drawEllipse(left_center, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)
            painter.drawEllipse(right_center, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)
            painter.drawEllipse(top_center, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)
            painter.drawEllipse(bottom_center, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)
            # painter.drawEllipse(origin, STRETCH_RECT_WIDTH, STRETCH_RECT_HEIGHT)

    def type(self):
        return self.UserType + 1

    def set_border_color(self, color):
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def set_fill_color(self, color):
        self.setBrush(color)

    def set_pen_width(self, pen_width):
        pen = self.pen()
        pen.setWidth(pen_width)
        self.setPen(pen)

    def set_pen_style(self, pen_style):
        pen = self.pen()
        pen.setStyle(pen_style)
        self.setPen(pen)

    def set_cap_style(self, cap_style):
        pen = self.pen()
        pen.setCapStyle(cap_style)
        self.setPen(pen)

    def set_join_style(self, join_style):
        pen = self.pen()
        pen.setJoinStyle(join_style)
        self.setPen(pen)
