from PyQt6.QtCore import Qt, QSize, QRect, pyqtSignal
from PyQt6.QtWidgets import (
    QGridLayout,
    QPushButton,
    QWidget,
    QRadioButton,
    QButtonGroup,
    QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QRegion, QColor

class CircularButton(QPushButton):
    def __init__(self, text, size, font_size, flag, parent=None):
        super().__init__(text, parent)

        self.setObjectName("controlbutton")

        self.flag = flag

        radius = size//2
        self.setFixedSize(QSize(size, size))
        self.setMask(QRegion(QRect(0, 0, size, size),
                                QRegion.RegionType.Ellipse))
        self.setStyleSheet(f"""
            border-radius: {radius}px;
            font-size: {font_size}px
""")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 200))

        self.setGraphicsEffect(shadow)

class OvalButton(QPushButton):
    def __init__(self, text, width, height, font_size, flag, parent=None):
        super().__init__(text, parent)

        self.setObjectName("controlbutton")

        self.flag = flag

        radius = width//2
        self.setFixedSize(QSize(width, height))

        self.setStyleSheet(f"""
            border-radius: {radius}px;
            font-size: {font_size}px
""")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 200))

        self.setGraphicsEffect(shadow)


class ModeSelector(QWidget):
    mode = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)

        self.voice_button = QRadioButton("Voice Control Mode")
        self.manual_button = QRadioButton("Manual Control Mode")

        self.voice_button.setFixedSize(QSize(300, 60))
        self.manual_button.setFixedSize(QSize(320, 60))

        self.button_group = QButtonGroup(self)
        self.button_group.addButton(self.voice_button, id=1)
        self.button_group.addButton(self.manual_button, id=2)

        self.voice_button.setChecked(True)

        layout.addWidget(self.voice_button, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.manual_button, 0, 1, alignment=Qt.AlignmentFlag.AlignLeft)

        layout.setColumnStretch(0, 5)
        layout.setColumnStretch(1, 5)

        self.button_group.idClicked.connect(self.on_mode_clicked)

    def on_mode_clicked(self, button_id):
        selected_mode = 'voice' if button_id == 1 else "manual"
        self.mode.emit(selected_mode)