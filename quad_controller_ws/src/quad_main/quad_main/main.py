import sys
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QFrame,
    QLabel,
    QStyle
)
from PyQt6.QtGui import QFont, QFontDatabase
from widgets import CircularButton, OvalButton, ModeSelector

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

        satoshi_black = self.external_font("Satoshi-Black.otf", 25)
        satoshi_medium = self.external_font("Satoshi-Medium.otf", 15)
        satoshi_black_large = self.external_font("Satoshi-Black.otf", 40)

        grid_layout = QGridLayout(self)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(0)

        system_panel = QFrame()
        system_panel.setObjectName("invisiblepanel")
        system_panel_layout = QHBoxLayout(system_panel)
        system_panel_layout.setContentsMargins(0, 0, 0, 0)
        system_panel_layout.setSpacing(0)

        status_panel = QFrame()
        status_panel.setObjectName("highlightedcontainer")
        status_panel.setFrameShadow(QFrame.Shadow.Raised)
        status_panel_layout = QVBoxLayout(status_panel)

        status_label = QLabel("System Online")
        status_label.setFont(satoshi_black)
        status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        status_label.setObjectName("blacklabel")
        status_panel_layout.addWidget(status_label, 1)

        status_sublabel = QLabel("All telemetry data is updated.")
        status_sublabel.setFont(satoshi_medium)
        status_sublabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        status_sublabel.setObjectName("blacklabel")
        status_panel_layout.addWidget(status_sublabel, 1)

        motion_panel = QFrame()
        motion_panel.setObjectName("transcontainer")
        motion_panel.setFrameShadow(QFrame.Shadow.Sunken)
        motion_panel_layout = QVBoxLayout(motion_panel)

        motion_label = QLabel("Hovering")
        motion_label.setFont(satoshi_black)
        motion_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        motion_label.setObjectName("whitelabel")
        motion_panel_layout.addWidget(motion_label, 1)

        motion_sublabel = QLabel("At (x, y, z)")
        motion_sublabel.setFont(satoshi_medium)
        motion_sublabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        motion_sublabel.setObjectName("whitelabel")
        motion_panel_layout.addWidget(motion_sublabel, 1)

        z_panel = QFrame()
        z_panel.setObjectName("transcontainer")
        z_panel.setFrameShadow(QFrame.Shadow.Sunken)
        z_panel_layout = QVBoxLayout(z_panel)

        z_label = QLabel("Level flight")
        z_label.setFont(satoshi_black)
        z_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        z_label.setObjectName("whitelabel")
        z_panel_layout.addWidget(z_label, 1)

        z_sublabel = QLabel("At z")
        z_sublabel.setFont(satoshi_medium)
        z_sublabel.setAlignment(Qt.AlignmentFlag.AlignLeft)
        z_sublabel.setObjectName("whitelabel")
        z_panel_layout.addWidget(z_sublabel, 1)

        system_panel_layout.addWidget(status_panel, 1)
        system_panel_layout.addWidget(motion_panel, 1)
        system_panel_layout.addWidget(z_panel, 1)

        control_panel = QFrame()
        control_panel.setObjectName("panel")
        control_panel.setFrameShadow(QFrame.Shadow.Raised)
        control_panel_layout = QGridLayout(control_panel)
        control_panel_layout.setSpacing(5)
        control_panel_layout.setContentsMargins(8, 8, 8, 8)

        stop = CircularButton("", 150, 75, "stop")
        forward = CircularButton("\u2B06", 120, 55, "forward")
        backward = CircularButton("\u2B07", 120, 55, "backward")
        left = CircularButton("\u2B05", 120, 55, "left")
        right = CircularButton("\u27A1", 120, 55, "right")
        up = OvalButton("\u2B06\n.\n.\n.\n.\n.\n.\n.\n.\n.\n.", 60, 300, 17, "up")
        down = OvalButton(".\n.\n.\n.\n.\n.\n.\n.\n.\n.\n\u2B07", 60, 300, 17, "down")

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
        bottom_panel_layout = QHBoxLayout(bottom_panel)

        mode_manager = ModeSelector()
        bottom_panel_layout.addWidget(mode_manager, 1)

        right_panel = QFrame()
        right_panel.setObjectName("panel")
        right_panel.setFrameShadow(QFrame.Shadow.Raised)
        right_panel_layout = QGridLayout(right_panel)

        motion_x_sublabel = QLabel("Angular velocity about x: 0 rad/s")
        motion_x_sublabel.setFont(satoshi_medium)
        motion_x_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        motion_x_sublabel.setObjectName("whitelabel")
        motion_panel_layout.addWidget(motion_x_sublabel, 1)

        motion_y_sublabel = QLabel("Angular velocity about y: 0 rad/s")
        motion_y_sublabel.setFont(satoshi_medium)
        motion_y_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        motion_y_sublabel.setObjectName("whitelabel")
        motion_panel_layout.addWidget(motion_y_sublabel, 1)

        motion_z_sublabel = QLabel("Angular velocity about z: 0 rad/s")
        motion_z_sublabel.setFont(satoshi_medium)
        motion_z_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        motion_z_sublabel.setObjectName("whitelabel")
        motion_panel_layout.addWidget(motion_z_sublabel, 1)

        x_ang_vel_panel = QFrame()
        x_ang_vel_panel.setObjectName("transcontainer")
        x_ang_vel_panel_layout = QVBoxLayout(x_ang_vel_panel)

        x_ang_vel_label = QLabel("0°")
        x_ang_vel_label.setFont(satoshi_black_large)
        x_ang_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        x_ang_vel_label.setObjectName("yellowlabel")
        x_ang_vel_panel_layout.addWidget(x_ang_vel_label, 1)

        x_ang_vel_sublabel = QLabel("About x axis")
        x_ang_vel_sublabel.setFont(satoshi_medium)
        x_ang_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        x_ang_vel_sublabel.setObjectName("yellowlabel")
        x_ang_vel_panel_layout.addWidget(x_ang_vel_sublabel, 1)

        y_ang_vel_panel = QFrame()
        y_ang_vel_panel.setObjectName("transcontainer")
        y_ang_vel_panel_layout = QVBoxLayout(y_ang_vel_panel)

        y_ang_vel_label = QLabel("0°")
        y_ang_vel_label.setFont(satoshi_black_large)
        y_ang_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        y_ang_vel_label.setObjectName("yellowlabel")
        y_ang_vel_panel_layout.addWidget(y_ang_vel_label, 1)

        y_ang_vel_sublabel = QLabel("About y axis")
        y_ang_vel_sublabel.setFont(satoshi_medium)
        y_ang_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        y_ang_vel_sublabel.setObjectName("yellowlabel")
        y_ang_vel_panel_layout.addWidget(y_ang_vel_sublabel, 1)

        z_ang_vel_panel = QFrame()
        z_ang_vel_panel.setObjectName("transcontainer")
        z_ang_vel_panel_layout = QVBoxLayout(z_ang_vel_panel)

        z_ang_vel_label = QLabel("0°")
        z_ang_vel_label.setFont(satoshi_black_large)
        z_ang_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        z_ang_vel_label.setObjectName("yellowlabel")
        z_ang_vel_panel_layout.addWidget(z_ang_vel_label, 1)

        z_ang_vel_sublabel = QLabel("About z axis")
        z_ang_vel_sublabel.setFont(satoshi_medium)
        z_ang_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        z_ang_vel_sublabel.setObjectName("yellowlabel")
        z_ang_vel_panel_layout.addWidget(z_ang_vel_sublabel, 1)

        right_panel_layout.addWidget(motion_x_sublabel, 1, 0)
        right_panel_layout.addWidget(motion_y_sublabel, 3, 0)
        right_panel_layout.addWidget(motion_z_sublabel, 5, 0)
        right_panel_layout.addWidget(x_ang_vel_panel, 0, 0)
        right_panel_layout.addWidget(y_ang_vel_panel, 2, 0)
        right_panel_layout.addWidget(z_ang_vel_panel, 4, 0)

        right_panel_layout.setRowStretch(0, 27)
        right_panel_layout.setRowStretch(1, 6)
        right_panel_layout.setRowStretch(2, 27)
        right_panel_layout.setRowStretch(3, 6)
        right_panel_layout.setRowStretch(4, 27)
        right_panel_layout.setRowStretch(5, 6)

        left_panel = QFrame()
        left_panel.setObjectName("panel")
        left_panel.setFrameShadow(QFrame.Shadow.Raised)
        left_panel_layout = QGridLayout(left_panel)
        left_panel_layout.setContentsMargins(0, 0, 0, 0)
        left_panel_layout.setSpacing(0)

        position_panel = QFrame()
        position_panel.setObjectName("highlightedcontainer")
        position_panel_layout = QVBoxLayout(position_panel)

        position_prelabel = QLabel("Position")
        position_prelabel.setFont(satoshi_black)
        position_prelabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        position_prelabel.setObjectName("blacklabel")
        position_panel_layout.addWidget(position_prelabel, 1)

        position_label = QLabel("(0, 0, 0)")
        position_label.setFont(satoshi_black_large)
        position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        position_label.setObjectName("blacklabel")
        position_panel_layout.addWidget(position_label, 1)

        position_sublabel = QLabel("In the Cartesian coordinate system")
        position_sublabel.setFont(satoshi_medium)
        position_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        position_sublabel.setObjectName("blacklabel")
        position_panel_layout.addWidget(position_sublabel, 1)

        x_vel_panel = QFrame()
        x_vel_panel.setObjectName("semihighlightedcontainer")
        x_vel_panel_layout = QVBoxLayout(x_vel_panel)

        x_vel_label = QLabel("0 m/s")
        x_vel_label.setFont(satoshi_black)
        x_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        x_vel_label.setObjectName("blacklabel")
        x_vel_panel_layout.addWidget(x_vel_label, 1)

        x_vel_sublabel = QLabel("In +x direction")
        x_vel_sublabel.setFont(satoshi_medium)
        x_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        x_vel_sublabel.setObjectName("blacklabel")
        x_vel_panel_layout.addWidget(x_vel_sublabel, 1)

        y_vel_panel = QFrame()
        y_vel_panel.setObjectName("semihighlightedcontainer")
        y_vel_panel_layout = QVBoxLayout(y_vel_panel)

        y_vel_label = QLabel("0 m/s")
        y_vel_label.setFont(satoshi_black)
        y_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        y_vel_label.setObjectName("blacklabel")
        y_vel_panel_layout.addWidget(y_vel_label, 1)

        y_vel_sublabel = QLabel("In +y direction")
        y_vel_sublabel.setFont(satoshi_medium)
        y_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        y_vel_sublabel.setObjectName("blacklabel")
        y_vel_panel_layout.addWidget(y_vel_sublabel, 1)

        z_vel_panel = QFrame()
        z_vel_panel.setObjectName("semihighlightedcontainer")
        z_vel_panel_layout = QVBoxLayout(z_vel_panel)

        z_vel_label = QLabel("0 m/s")
        z_vel_label.setFont(satoshi_black)
        z_vel_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        z_vel_label.setObjectName("blacklabel")
        z_vel_panel_layout.addWidget(z_vel_label, 1)

        z_vel_sublabel = QLabel("In +z direction")
        z_vel_sublabel.setFont(satoshi_medium)
        z_vel_sublabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        z_vel_sublabel.setObjectName("blacklabel")
        z_vel_panel_layout.addWidget(z_vel_sublabel, 1)

        left_panel_layout.addWidget(position_panel, 0, 0)
        left_panel_layout.addWidget(x_vel_panel, 1, 0)
        left_panel_layout.addWidget(y_vel_panel, 2, 0)
        left_panel_layout.addWidget(z_vel_panel, 3, 0)

        left_panel_layout.setRowStretch(0, 4)
        left_panel_layout.setRowStretch(1, 2)
        left_panel_layout.setRowStretch(2, 2)
        left_panel_layout.setRowStretch(3, 2)
        
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

    def external_font(self, font_path, font_size):
        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            font_family = font_families[0]
            custom_font = QFont(font_family, font_size, QFont.Weight.Bold)
        else:
            custom_font = QFont("Sans-Serif", font_size)

        return custom_font


if __name__=="__main__":
    app = QApplication(sys.argv)

    style = load_stylesheet("style.qss")
    app.setStyleSheet(style)

    window = TelemetryDashboard()
    window.show()

    sys.exit(app.exec())