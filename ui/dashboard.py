import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
import cv2

from logic.autonomous_flow import run_autonomous_cycle, CAMERA
from logic.camera_module import convert_frame_to_opencv

class LiveFeedDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rotation System – Autonome Cycle")
        self.setGeometry(100, 100, 1200, 800)

        # Cameravenster
        self.image_label = QLabel()
        self.image_label.setFixedSize(800, 600)
        self.image_label.setStyleSheet("border: 2px solid gray")

        # Startknop
        self.start_button = QPushButton("Start Cycle")
        self.start_button.setFixedHeight(40)
        self.start_button.clicked.connect(self.run_cycle)

        # Statuslogs
        self.status_output = QTextEdit()
        self.status_output.setReadOnly(True)
        self.status_output.setStyleSheet("font-family: Consolas; font-size: 12px;")

        # Layout
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("System Logs"))
        right_layout.addWidget(self.status_output)
        right_layout.addWidget(self.start_button)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

        # Live camerafeed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)
        self.timer.start(100)

    def run_cycle(self):
        run_autonomous_cycle()

    def update_camera_frame(self):
        if CAMERA is None:
            return
        _, raw_frame = CAMERA.MV_CC_GetOneFrameTimeout(2000)
        if raw_frame is None:
            return
        image = convert_frame_to_opencv(raw_frame)
        if image is not None:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(q_image))

# Globale referentie om logstatus te kunnen bijwerken
DASHBOARD_INSTANCE = None

def start_dashboard():
    global DASHBOARD_INSTANCE
    app = QApplication(sys.argv)
    dashboard = LiveFeedDashboard()
    DASHBOARD_INSTANCE = dashboard
    dashboard.show()
    sys.exit(app.exec_())

def update_dashboard_status(text):
    if DASHBOARD_INSTANCE:
        DASHBOARD_INSTANCE.status_output.append(text)
    print(text)
