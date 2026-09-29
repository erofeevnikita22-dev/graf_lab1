"""Проверка действий пользователя без графического рабочего стола."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import tempfile
import unittest
from pathlib import Path
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QApplication
from main import LabWindow


class LabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.window = LabWindow()
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()

    def test_text_image_text_by_click(self):
        original = self.window.label.text()
        self.assertTrue(original)
        QTest.mouseClick(self.window.image_button, Qt.LeftButton)
        self.assertEqual(self.window.label.text(), "")
        self.assertFalse(self.window.label.pixmap().isNull())
        QTest.mouseClick(self.window.image_button, Qt.LeftButton)
        self.assertEqual(self.window.label.text(), original)
        pixmap = self.window.label.pixmap()
        self.assertTrue(pixmap is None or pixmap.isNull())

    def test_shape_alpha_and_reset(self):
        self.assertTrue(self.window.mask().isEmpty())
        QTest.mouseClick(self.window.shape_button, Qt.LeftButton)
        self.assertFalse(self.window.mask().contains(QPoint(0, 0)))
        self.assertTrue(self.window.mask().contains(self.window.rect().center()))
        alpha = self.window.shape.toImage().pixelColor(340, 230).alpha()
        self.assertGreater(alpha, 0)
        self.assertLess(alpha, 255)
        # Элементы управления целиком остаются внутри видимой формы.
        for widget in (self.window.image_button, self.window.shape_button,
                       self.window.close_button):
            self.assertTrue(self.window.mask().contains(widget.geometry()))
        QTest.mouseClick(self.window.shape_button, Qt.LeftButton)
        self.assertTrue(self.window.mask().isEmpty())

    def test_buttons_work_in_both_shapes(self):
        for _ in range(4):
            QTest.mouseClick(self.window.shape_button, Qt.LeftButton)
            QTest.mouseClick(self.window.image_button, Qt.LeftButton)
            self.assertEqual(self.window.shaped, self.window.image_visible)

    def test_keyboard_activation_and_close(self):
        self.window.image_button.setFocus()
        QTest.keyClick(self.window.image_button, Qt.Key_Space)
        self.assertTrue(self.window.image_visible)
        QTest.keyClick(self.window, Qt.Key_Escape)
        self.assertFalse(self.window.isVisible())

    def test_close_button(self):
        QTest.mouseClick(self.window.close_button, Qt.LeftButton)
        self.assertFalse(self.window.isVisible())

    def test_missing_assets(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaisesRegex(ValueError, "не удалось загрузить"):
                LabWindow(Path(folder))


if __name__ == "__main__":
    unittest.main()
