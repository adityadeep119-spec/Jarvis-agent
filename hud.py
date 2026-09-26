import sys
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication, QLabel, QWidget


class JarvisHUD(QWidget):
    status_signal = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.WindowTransparentForInput
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel("JARVIS: STANDBY", self)
        self.label.setStyleSheet(
            "color: #00FFFF; font-size: 14px; font-weight: bold; "
            "background-color: rgba(10, 10, 20, 180); padding: 8px 14px; "
            "border: 1px solid #00FFFF; border-radius: 8px;"
        )

        # Position top right (adjust x, y according to your monitor resolution)
        self.setGeometry(1500, 50, 250, 50)

        # Connect thread-safe signal
        self.status_signal.connect(self._update_text)

    def _update_text(self, text):
        colors = {
            "STANDBY": "color: #00FFFF; border-color: #00FFFF;",
            "LISTENING": "color: #FF3333; border-color: #FF3333;",
            "PROCESSING": "color: #FFCC00; border-color: #FFCC00;",
            "SPEAKING": "color: #00FF66; border-color: #00FF66;",
        }
        style = colors.get(text, "color: white; border-color: white;")
        self.label.setText(f"JARVIS: {text}")
        self.label.setStyleSheet(
            f"{style} font-size: 14px; font-weight: bold; "
            "background-color: rgba(10, 10, 20, 180); padding: 8px 14px; border-radius: 8px;"
        )

    def set_status(self, status):
        """Thread-safe status update function."""
        self.status_signal.emit(status)