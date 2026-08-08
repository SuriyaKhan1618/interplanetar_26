import sys
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QStyle
)
from widgets import CircularButton, OvalButton

def load_stylesheet(filename):
    with open(filename, "r") as f:
        return f.read()


class TelemetryDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Quadrotor Control Station")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setObjectName("mainwindow")

        screen = QApplication.primaryScreen().availableGeometry()
        width = screen.width()
        height = screen.height()

        self.resize(width, height)

        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)

        system_panel = QFrame()
        system_panel.setObjectName("invisiblepanel")
        system_panel_layout = QHBoxLayout(system_panel)
        system_panel_layout.addStretch()

        control_panel = QFrame()
        control_panel.setObjectName("panel")
        control_panel.setFrameShadow(QFrame.Shadow.Raised)
        control_panel_layout = QGridLayout(control_panel)
        control_panel_layout.setSpacing(5)
        control_panel_layout.setContentsMargins(8, 8, 8, 8)

        stop = CircularButton("", 150, 75)
        forward = CircularButton("\u2B06", 120, 55)
        backward = CircularButton("\u2B07", 120, 55)
        left = CircularButton("\u2B05", 120, 55)
        right = CircularButton("\u27A1", 120, 55)
        up = OvalButton("\u2B06\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.", 60, 300, 17)
        down = OvalButton(".\n.\n.\n.\n.\n.\n.\n.\n.\n.\n\u2B07", 60, 300, 17)

        pause_icon = stop.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
        stop.setIcon(pause_icon)
        stop.setIconSize(QSize(150, 150))

        control_panel_layout.addWidget(up, 0, 0, 3, 1, alignment=Qt.AlignmentFlag.AlignRight)
        control_panel_layout.addWidget(stop, 1, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        control_panel_layout.addWidget(forward, 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        control_panel_layout.addWidget(backward, 2, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        control_panel_layout.addWidget(left, 1, 1, alignment=Qt.AlignmentFlag.AlignRight)
        control_panel_layout.addWidget(right, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        control_panel_layout.addWidget(down, 0, 4, 3, 1, alignment=Qt.AlignmentFlag.AlignLeft)        

        control_panel_layout.setRowStretch(0, 3)
        control_panel_layout.setRowStretch(1, 4)
        control_panel_layout.setRowStretch(2, 3)
        control_panel_layout.setColumnStretch(0, 1)
        control_panel_layout.setColumnStretch(1, 2)
        control_panel_layout.setColumnStretch(2, 4)
        control_panel_layout.setColumnStretch(3, 2)
        control_panel_layout.setColumnStretch(4, 1)

        bottom_panel = QFrame()
        bottom_panel.setObjectName("invisiblepanel")
        bottom_panel_layout = QGridLayout(bottom_panel)
        bottom_panel_layout.setSpacing(5)
        bottom_panel_layout.setContentsMargins(8, 8, 8, 8)

        bottom_panel_layout.setColumnStretch(0, 5)
        bottom_panel_layout.setColumnStretch(1, 5)

        right_panel = QFrame()
        right_panel.setObjectName("panel")
        right_panel.setFrameShadow(QFrame.Shadow.Raised)
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.addStretch()

        left_panel = QFrame()
        left_panel.setObjectName("panel")
        left_panel.setFrameShadow(QFrame.Shadow.Raised)
        left_panel_layout = QVBoxLayout(left_panel)
        left_panel_layout.addStretch()        

        grid_layout.addWidget(right_panel, 0, 0, 3, 1)
        grid_layout.addWidget(system_panel, 0, 1)
        grid_layout.addWidget(control_panel, 1, 1)
        grid_layout.addWidget(bottom_panel, 2, 1)
        grid_layout.addWidget(left_panel, 0, 2, 3, 1)

        grid_layout.setRowStretch(0, 2)
        grid_layout.setRowStretch(1, 7)
        grid_layout.setRowStretch(2, 1)
        grid_layout.setColumnStretch(0, 2)
        grid_layout.setColumnStretch(1, 6)
        grid_layout.setColumnStretch(2, 2)


if __name__=="__main__":
    app = QApplication(sys.argv)

    style = load_stylesheet("style.qss")
    app.setStyleSheet(style)

    window = TelemetryDashboard()
    window.show()

    sys.exit(app.exec())