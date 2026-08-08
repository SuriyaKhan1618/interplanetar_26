from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtGui import QRegion, QColor

class CircularButton(QPushButton):
    def __init__(self, text, size, font_size, parent=None):
        super().__init__(text, parent)

        self.setObjectName("controlbutton")
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
    def __init__(self, text, width, height, font_size, parent=None):
        super().__init__(text, parent)

        self.setObjectName("controlbutton")
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