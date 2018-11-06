import sys
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolButton, QMenu, QDialog, QColorDialog
from main_window import Ui_MainWindow
from pen_properties_dialog import Ui_PenPropertiesDialog
from item import Line, Rectangle
from scene import Scene


class Signal(QObject):
    set_cur_shape = pyqtSignal(QGraphicsItem)
    set_clip_area = pyqtSignal(QGraphicsItem)


class View(QGraphicsView):

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.scale_factor = 1.0
        self.zoom_delta = 0.1

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Equal:
            self.zoom_in()
        elif event.key() == Qt.Key_Minus:
            self.zoom_out()
        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        scroll_amount = event.angleDelta()
        if scroll_amount.y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def zoom_in(self):
        self.zoom(1 + self.zoom_delta)

    def zoom_out(self):
        self.zoom(1 - self.zoom_delta)

    def zoom(self, scale_factor):
        factor = self.transform().scale(scale_factor, scale_factor).mapRect(QRectF(0, 0, 1, 1)).width()
        if factor < 0.07 or factor > 100:
            return
        self.scale(scale_factor, scale_factor)
        self.scale_factor = self.scale_factor * scale_factor


class MainWindow(QMainWindow, Ui_MainWindow):

    release = True
    cur_pos = None
    file_name = None

    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setWindowOpacity(0.5)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self.signal = Signal()

        self._translate = QCoreApplication.translate

        self.select_tool_button = QToolButton(self)
        self.select_rectangle_action = QAction(self)
        self.select_ellipse_action = QAction(self)

        self.shape_tool_button = QToolButton(self)
        self.shape_line_action = QAction(self)
        self.shape_rectangle_action = QAction(self)
        self.shape_ellipse_action = QAction(self)
        self.shape_polygon_action = QAction(self)

        self.color_dialog = QColorDialog(self)
        self.pen_properties_dialog = QDialog(self, Qt.WindowTitleHint | Qt.WindowSystemMenuHint)
        self.ui_pen_properties_dialog = Ui_PenPropertiesDialog()
        self.ui_pen_properties_dialog.setupUi(self.pen_properties_dialog)
        self.ui_pen_properties_dialog.pen_width_spin_box.valueChanged.connect(
            self.ui_pen_properties_dialog.pen_width_slider.setValue)
        self.ui_pen_properties_dialog.pen_width_slider.valueChanged.connect(
            self.ui_pen_properties_dialog.pen_width_spin_box.setValue)

        self.scene = Scene(self)
        self.scene.setSceneRect(0, 0, 640, 399)
        self.view = View(self.scene, self)
        self.setCentralWidget(self.view)

        self.set_select_tool_button()
        self.set_shape_tool_button()

        self.actionBorder_Color.triggered.connect(self.show_color_dialog)
        self.actionFill_Color.triggered.connect(self.show_color_dialog)
        self.actionPattern.triggered.connect(self.show_pen_properties_dialog)
        self.actionZoom_In.triggered.connect(self.view.zoom_in)
        self.actionZoom_Out.triggered.connect(self.view.zoom_out)
        self.shape_line_action.triggered.connect(self.emit_set_cur_shape_signal)
        self.shape_rectangle_action.triggered.connect(self.emit_set_cur_shape_signal)
        self.select_rectangle_action.triggered.connect(self.emit_set_clip_area_signal)
        self.select_ellipse_action.triggered.connect(self.emit_set_clip_area_signal)
        self.actionClip.triggered.connect(self.scene.clip)
        self.actionNew.triggered.connect(self.new)
        self.actionSave.triggered.connect(self.save)
        self.actionOpen.triggered.connect(self.open)
        self.signal.set_cur_shape.connect(self.scene.set_cur_shape)
        self.signal.set_clip_area.connect(self.scene.set_clip_area)

    def new(self):
        self.file_name = QFileDialog.getSaveFileName(None, "保存为", "./",
                                                     "Image Files (*.png *.jpg *.bmp)")
        if self.file_name[0]:
            image = self.view.grab()
            image.save(self.file_name[0])

    def save(self):
        if self.file_name:
            file_name = self.file_name
        else:
            file_name = QFileDialog.getSaveFileName(None, "保存为", "./",
                                                    "Image Files (*.png *.jpg *.bmp)")
            self.file_name = file_name

        if file_name[0]:
            self.view.scene().clearSelection()
            if self.view.scene().clip_area is not None:
                self.view.scene().removeItem(self.view.scene().clip_area)
                self.view.scene().clip_area = None
            image = self.view.grab()
            image.save(file_name[0])

    def open(self):
        file_name = QFileDialog.getOpenFileName(None, "打开", "./",
                                                "Image Files (*.png *.jpg *.bmp)")
        if file_name[0]:
            self.file_name = file_name
            background = QGraphicsPixmapItem(QPixmap(file_name[0]))
            background.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
            background.setPos(self.view.scene().width() / 2 - background.pixmap().width() / 2,
                              self.view.scene().height() / 2 - background.pixmap().height() / 2)
            self.view.scene().addItem(background)

    def show_color_dialog(self):
        sender = self.sender()
        self.color_dialog.show()
        color = self.color_dialog.getColor(Qt.black)
        selected_items = self.scene.selectedItems()
        if color.isValid():
            if sender.objectName() == "actionBorder_Color":
                self.scene.border_color = color
                for item in selected_items:
                    item.set_border_color(color)
            elif sender.objectName() == "actionFill_Color":
                self.scene.fill_color = color
                for item in selected_items:
                    item.set_fill_color(color)

    def show_pen_properties_dialog(self):
        self.pen_properties_dialog.setVisible(True)
        if self.pen_properties_dialog.exec_():
            selected_items = self.scene.selectedItems()
            self.scene.pen_width = self.ui_pen_properties_dialog.pen_width_slider.value()
            pen_style = self.ui_pen_properties_dialog.pen_style_combo_box.currentText()
            cap_style = self.ui_pen_properties_dialog.cap_style_combo_box.currentText()
            join_style = self.ui_pen_properties_dialog.join_style_combo_box.currentText()
            if pen_style == "SolidLine":
                self.scene.pen_style = Qt.SolidLine
            elif pen_style == "DashLine":
                self.scene.pen_style = Qt.DashLine
            elif pen_style == "DotLine":
                self.scene.pen_style = Qt.DotLine
            elif pen_style == "DashDotLine":
                self.scene.pen_style = Qt.DashDotLine
            elif pen_style == "DashDotDotLine":
                self.scene.pen_style = Qt.DashDotDotLine
            if cap_style == "SquareCap":
                self.scene.cap_style = Qt.SquareCap
            elif cap_style == "FlatCap":
                self.scene.cap_style = Qt.FlatCap
            elif cap_style == "RoundCap":
                self.scene.cap_style = Qt.RoundCap
            if join_style == "BevelJoin":
                self.scene.join_style = Qt.BevelJoin
            elif join_style == "MiterJoin":
                self.scene.join_style = Qt.MiterJoin
            elif join_style == "RoundJoin":
                self.scene.join_style = Qt.RoundJoin

            for item in selected_items:
                item.set_pen_width(self.scene.pen_width)
                item.set_pen_style(self.scene.pen_style)
                item.set_cap_style(self.scene.cap_style)
                item.set_join_style(self.scene.join_style)

    def emit_set_cur_shape_signal(self):
        sender = self.sender()
        if sender.text() == "线条":
            self.signal.set_cur_shape.emit(Line())
        elif sender.text() == "矩形":
            self.signal.set_cur_shape.emit(Rectangle())
        self.update()

    def emit_set_clip_area_signal(self):
        sender = self.sender()
        if sender.text() == "矩形选择":
            self.signal.set_clip_area.emit(Rectangle())
        elif sender.text() == "椭圆选择":
            pass
        self.update()

    def set_select_tool_button(self):
        self.select_tool_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.select_tool_button.setToolTip("选择工具")
        self.select_tool_button.setPopupMode(QToolButton.InstantPopup)
        self.select_tool_button.setText("选择工具")
        self.select_tool_button.setStatusTip("选择工具")
        select_icon = QIcon()
        select_icon.addPixmap(QPixmap(":/image/images/icons8-选择无-100.png"), QIcon.Normal, QIcon.Off)
        self.select_tool_button.setIcon(select_icon)
        self.select_tool_button.setAutoRaise(True)
        self.toolBar.insertWidget(self.actionClip, self.select_tool_button).setVisible(True)

        select_rectangle_icon = QIcon()
        select_rectangle_icon.addPixmap(QPixmap(":/image/images/icons8-选择无-100.png"), QIcon.Normal, QIcon.Off)
        self.select_rectangle_action.setIcon(select_rectangle_icon)
        self.select_rectangle_action.setObjectName("actionSelect_Rectangle")
        self.select_rectangle_action.setText(self._translate("MainWindow", "矩形选择"))
        self.select_rectangle_action.setStatusTip(self._translate("MainWindow", "矩形选择"))

        select_ellipse_icon = QIcon()
        select_ellipse_icon.addPixmap(QPixmap(":/image/images/icons8-椭圆-100.png"), QIcon.Normal, QIcon.Off)
        self.select_ellipse_action.setIcon(select_ellipse_icon)
        self.select_ellipse_action.setObjectName("actionSelect_Ellipse")
        self.select_ellipse_action.setText(self._translate("MainWindow", "椭圆选择"))
        self.select_ellipse_action.setStatusTip(self._translate("MainWindow", "椭圆选择"))

        select_menu = QMenu(self)
        select_menu.addAction(self.select_rectangle_action)
        select_menu.addAction(self.select_ellipse_action)
        self.select_tool_button.setMenu(select_menu)

    def set_shape_tool_button(self):

        self.shape_tool_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.shape_tool_button.setToolTip("形状")
        self.shape_tool_button.setPopupMode(QToolButton.InstantPopup)
        self.shape_tool_button.setText("形状")
        self.shape_tool_button.setStatusTip("形状")
        shape_icon = QIcon()
        shape_icon.addPixmap(QPixmap(":/image/images/icons8-改变形状-100.png"), QIcon.Normal, QIcon.Off)
        self.shape_tool_button.setIcon(shape_icon)
        self.shape_tool_button.setAutoRaise(True)
        self.toolBar.insertWidget(self.actionChange_Color, self.shape_tool_button).setVisible(True)

        shape_line_icon = QIcon()
        shape_line_icon.addPixmap(QPixmap(":/image/images/icons8-线-80.png"), QIcon.Normal, QIcon.Off)
        self.shape_line_action.setIcon(shape_line_icon)
        self.shape_line_action.setObjectName("actionShape_Line")
        self.shape_line_action.setText(self._translate("MainWindow", "线条"))
        self.shape_line_action.setStatusTip(self._translate('MainWindow', "线条"))

        shape_rectangle_icon = QIcon()
        shape_rectangle_icon.addPixmap(QPixmap(":/image/images/icons8-圆角矩形笔画-96.png"), QIcon.Normal, QIcon.Off)
        self.shape_rectangle_action.setIcon(shape_rectangle_icon)
        self.shape_rectangle_action.setObjectName("actionShape_Rectangle")
        self.shape_rectangle_action.setText(self._translate("MainWindow", "矩形"))
        self.shape_rectangle_action.setStatusTip(self._translate("MainWindow", "矩形"))

        shape_ellipse_icon = QIcon()
        shape_ellipse_icon.addPixmap(QPixmap(":/image/images/icons8-椭圆一笔画-100.png"), QIcon.Normal, QIcon.Off)
        self.shape_ellipse_action.setIcon(shape_ellipse_icon)
        self.shape_ellipse_action.setObjectName("actionShape_Ellipse")
        self.shape_ellipse_action.setText(self._translate("MainWindow", "椭圆"))
        self.shape_ellipse_action.setStatusTip(self._translate("MainWindow", "椭圆"))

        shape_polygon_icon = QIcon()
        shape_polygon_icon.addPixmap(QPixmap(":/image/images/icons8-多边形-100.png"), QIcon.Normal, QIcon.Off)
        self.shape_polygon_action.setIcon(shape_polygon_icon)
        self.shape_polygon_action.setObjectName("actionShape_Polygon")
        self.shape_polygon_action.setText(self._translate("MainWindow", "多边形"))
        self.shape_polygon_action.setStatusTip(self._translate("MainWindow", "多边形"))

        shape_menu = QMenu(self)
        shape_menu.addAction(self.shape_line_action)
        shape_menu.addAction(self.shape_rectangle_action)
        shape_menu.addAction(self.shape_ellipse_action)
        shape_menu.addAction(self.shape_polygon_action)
        self.shape_tool_button.setMenu(shape_menu)

    """
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.release = False
            self.cur_pos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.release:
            self.move(event.pos() - self.cur_pos + self.pos())

    def mouseReleaseEvent(self, event):
        self.release = True
    """


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
