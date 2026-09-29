import sys
from pathlib import Path

import PyQt5
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QColor, QPainter, QPixmap, QRegion
from PyQt5.QtWidgets import (
    QApplication, QHBoxLayout, QLabel, QMessageBox, QPushButton,
    QVBoxLayout, QWidget,
)

ASSETS = Path(__file__).resolve().parent / "assets"


def load_pixmap(path):
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        raise ValueError(f"не удалось загрузить изображение\n{path}")
    return pixmap


class LabWindow(QWidget):
    def __init__(self, assets_dir=ASSETS):
        super().__init__()
        self.picture = load_pixmap(assets_dir / "picture.png")
        self.shape = load_pixmap(assets_dir / "window_shape.png")
        self.image_visible = False
        self.shaped = False
        self.drag_offset = None

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowTitle("лабораторная работа № 1")
        self.setFixedSize(self.shape.size())

        title = QLabel("лабораторная работа № 1")
        title.setAttribute(Qt.WA_TransparentForMouseEvents)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(34, 32)
        self.close_button.setStyleSheet("padding: 0; font-size: 20px;")
        self.close_button.setAccessibleName("закрыть окно")
        self.close_button.setToolTip("закрыть")
        self.close_button.clicked.connect(self.close)
        header = QHBoxLayout()
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.close_button)

        self.label = QLabel("нажмите кнопку, чтобы показать изображение")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setMinimumHeight(220)
        self.label.setAccessibleName("надпись или изображение")
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.image_button = QPushButton("показать изображение")
        self.shape_button = QPushButton("изменить форму окна")
        self.image_button.clicked.connect(self.toggle_image)
        self.shape_button.clicked.connect(self.toggle_shape)
        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addWidget(self.image_button)
        buttons.addWidget(self.shape_button)

        hint = QLabel("")
        hint.setAlignment(Qt.AlignCenter)
        hint.setAttribute(Qt.WA_TransparentForMouseEvents)
        hint.setStyleSheet("font-size: 12px; color: #526174;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(64, 48, 64, 48)
        layout.setSpacing(18)
        layout.addLayout(header)
        layout.addWidget(self.label, 1)
        layout.addLayout(buttons)
        layout.addWidget(hint)
        self.setStyleSheet("""
            QLabel { color: #182a40; font-size: 15px; background: transparent; }
            QPushButton { background: #285bd4; color: white; border: none;
                          border-radius: 6px; padding: 12px 10px; font-size: 13px; }
            QPushButton:hover { background: #214bae; }
            QPushButton:pressed { background: #193a87; }
            QPushButton:focus { border: 2px solid #101f38; }
        """)

    def toggle_image(self):
        self.image_visible = not self.image_visible
        if self.image_visible:
            self.label.setPixmap(self.picture.scaled(
                340, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.image_button.setText("вернуть надпись")
        else:
            self.label.setText("нажмите кнопку, чтобы показать изображение")
            self.image_button.setText("показать изображение")

    def toggle_shape(self):
        self.shaped = not self.shaped
        if self.shaped:
            self.setMask(QRegion(self.shape.mask()))
            self.shape_button.setText("вернуть прямоугольник")
        else:
            self.clearMask()
            self.shape_button.setText("изменить форму окна")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.shaped:
            painter.drawPixmap(0, 0, self.shape)
        else:
            painter.fillRect(self.rect(), QColor("#f3f6fc"))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_offset)
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.drag_offset = None
        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


def main():
    plugins_path = Path(PyQt5.__file__).resolve().parent / "Qt5" / "plugins"
    QCoreApplication.setLibraryPaths([str(plugins_path)])

    app = QApplication(sys.argv)
    try:
        window = LabWindow()
    except ValueError as error:
        QMessageBox.critical(None, "ошибка загрузки ресурсов", str(error))
        return 1
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
