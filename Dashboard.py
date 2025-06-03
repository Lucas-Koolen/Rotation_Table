import sys
import serial
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QGroupBox
)
from PyQt5.QtCore import QTimer

class UltraCalDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultra Calibratie Dashboard")
        self.setGeometry(100, 100, 800, 800)

        try:
            self.ser = serial.Serial('COM7', 9600, timeout=1)
            time.sleep(2)
            print("Verbonden met COM7")
        except serial.SerialException:
            print("FOUT: COM7 is niet beschikbaar.")
            sys.exit(1)

        layout = QVBoxLayout()

        self.servos = [
            (0, "Lopende Band 1", "dir"),
            (1, "Draaitafel 1", "rotate"),
            (2, "Pusher 1", "pusher"),
            (3, "L1 (graden)", "pos3"),
            (4, "L2 (graden)", "pos3"),
            (5, "Lopende Band 2", "dir"),
            (6, "Pusher 2", "pusher"),
            (7, "Draaitafel 2", "rotate")
        ]

        for servo_num, name, s_type in self.servos:
            group = QGroupBox(f"{name} (Servo {servo_num})")
            group_layout = QVBoxLayout()

            if s_type == "dir":
                group_layout.addLayout(self.add_directional_controls(servo_num))
            elif s_type == "rotate":
                group_layout.addLayout(self.add_rotation_controls(servo_num))
            elif s_type == "pos":
                group_layout.addLayout(self.add_position_controls(servo_num))
            elif s_type == "pos3":
                group_layout.addLayout(self.add_fixed_position_controls(servo_num))
            elif s_type == "pusher":
                group_layout.addLayout(self.add_pusher_controls(servo_num))

            group.setLayout(group_layout)
            layout.addWidget(group)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log_output)

        # Eindschakelaar-status
        self.endstop_label = QLabel("Endstops: onbekend")
        layout.addWidget(self.endstop_label)

        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_endstop_status)
        self.status_timer.start(1000)  # elke seconde

        self.setLayout(layout)

    def log(self, message):
        self.log_output.append(message)
        print(message)

    def send_command(self, cmd):
        try:
            self.ser.write((cmd + '\n').encode())
            self.log(f"Verstuurd: {cmd}")
        except serial.SerialException:
            self.log("FOUT bij verzenden.")

    def update_endstop_status(self):
        try:
            self.ser.write(b'GET ENDSTOPS\n')
            line = self.ser.readline().decode().strip()
            if line.startswith("ENDSTOP_STATUS"):
                _, p1, p2 = line.split()
                status = f"Pusher 1: {'INGEDRUKT' if p1 == '1' else 'open'}, Pusher 2: {'INGEDRUKT' if p2 == '1' else 'open'}"
                self.endstop_label.setText(f"Endstops: {status}")
        except Exception:
            self.endstop_label.setText("Endstops: fout")

    def add_directional_controls(self, servo):
        row = QHBoxLayout()
        for label, cmd in [("Vooruit", "FWD"), ("Achteruit", "REV"), ("Stop", "STOP")]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, c=cmd: self.send_command(f"SET {servo} {c}"))
            row.addWidget(btn)
        return row

    def add_rotation_controls(self, servo):
        row = QHBoxLayout()
        angle_input = QLineEdit()
        angle_input.setPlaceholderText("Graden (-360 tot 360)")
        btn_fwd = QPushButton("Draaien FWD")
        btn_rev = QPushButton("Draaien REV")

        btn_fwd.clicked.connect(lambda: self.send_command(f"ROTATE {servo} {angle_input.text()} FWD"))
        btn_rev.clicked.connect(lambda: self.send_command(f"ROTATE {servo} {angle_input.text()} REV"))

        row.addWidget(angle_input)
        row.addWidget(btn_fwd)
        row.addWidget(btn_rev)
        return row

    def add_position_controls(self, servo):
        row = QHBoxLayout()
        angle_input = QLineEdit()
        angle_input.setPlaceholderText("Graden (0–180)")
        btn_send = QPushButton("Verstuur")
        btn_send.clicked.connect(lambda: self.send_command(f"POS {servo} {angle_input.text()}"))
        row.addWidget(angle_input)
        row.addWidget(btn_send)
        return row

    def add_fixed_position_controls(self, servo):
        row = QHBoxLayout()
        if servo == 3:
            pos_dict = {"Weg": 0, "Box Enter": 105, "Box Out": 210}
        elif servo == 4:
            pos_dict = {"Weg": 210, "Box Enter": 0, "Box Out": 110}
        else:
            pos_dict = {}

        for label, angle in pos_dict.items():
            btn = QPushButton(label)
            btn.clicked.connect(lambda _, a=angle: self.send_command(f"POS {servo} {a}"))
            row.addWidget(btn)
        return row

    def add_pusher_controls(self, servo):
        row = QHBoxLayout()
        time_input = QLineEdit()
        time_input.setPlaceholderText("ms voor vooruit (wegduwen)")
        btn_fwd = QPushButton("Vooruit (time)")         # Weg van endstop
        btn_rev = QPushButton("Achteruit (auto-stop)")  # Richting endstop
        btn_stop = QPushButton("Stop")

        btn_fwd.clicked.connect(lambda: self.send_command(f"SET {servo} FWD {time_input.text()}"))
        btn_rev.clicked.connect(lambda: self.send_command(f"SET {servo} REV"))
        btn_stop.clicked.connect(lambda: self.send_command(f"SET {servo} STOP"))

        row.addWidget(time_input)
        row.addWidget(btn_fwd)
        row.addWidget(btn_rev)
        row.addWidget(btn_stop)
        return row

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UltraCalDashboard()
    window.show()
    sys.exit(app.exec_())
