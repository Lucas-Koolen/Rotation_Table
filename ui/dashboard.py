import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPixmap, QImage
import cv2

import logic.autonomous_flow as autonomous_flow
from logic.autonomous_flow import run_autonomous_cycle
from logic.camera_module import convert_frame_to_opencv, init_camera
from sensor.height_sensor import HeightSensorReader


class LiveFeedDashboard(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize camera and height sensor once
        if autonomous_flow.CAMERA is None:
            autonomous_flow.CAMERA = init_camera()
        if autonomous_flow.HEIGHT_READER is None:
            autonomous_flow.HEIGHT_READER = HeightSensorReader()
        self.setWindowTitle("Rotation System – Autonome Cycle")
        self.setGeometry(100, 100, 1200, 800)

        self.setStyleSheet(
            """
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
            }
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ccc;
            }
            QPushButton {
                background-color: #007ACC;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                margin-bottom: 20px;
            }
            """
        )

        self.title_label = QLabel("Rotation System – Autonome Cycle")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setAlignment(Qt.AlignCenter)

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
        self.status_output.setStyleSheet(
            "font-family: 'Consolas', monospace; font-size: 12px;"
        )

        # Layout
        right_layout = QVBoxLayout()
        logs_label = QLabel("System Logs")
        logs_label.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(logs_label)
        right_layout.addWidget(self.status_output)
        right_layout.addStretch()
        right_layout.addWidget(self.start_button)

        content_layout = QHBoxLayout()
        content_layout.addWidget(self.image_label)
        content_layout.addLayout(right_layout)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(content_layout)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.setLayout(main_layout)

        # Live camerafeed
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_camera_frame)
        self.timer.start(100)

    def run_cycle(self):
        run_autonomous_cycle()

    def update_camera_frame(self):
        if autonomous_flow.CAMERA is None:
            return
        frame_tuple = autonomous_flow.CAMERA.MV_CC_GetOneFrameTimeout(2000)
        if not frame_tuple:
            return
        image = convert_frame_to_opencv(frame_tuple)
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
