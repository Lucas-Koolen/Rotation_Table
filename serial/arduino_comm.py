import serial
import time
from config.config import SERIAL_PORT, BAUD_RATE

class ArduinoComm:
    def __init__(self):
        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            time.sleep(2)  # Wacht op Arduino-reset
            print(f"[SERIAL] Verbonden met Arduino op {SERIAL_PORT}")
        except serial.SerialException:
            print(f"[SERIAL ERROR] Geen verbinding op {SERIAL_PORT}")
            self.ser = None

    def send_command(self, command):
        if not self.ser:
            print("[SERIAL] Geen verbinding.")
            return None

        try:
            self.ser.write((command + "\n").encode())
            print(f"[TX] {command}")

            response = self.ser.readline().decode().strip()
            print(f"[RX] {response}")
            return response
        except Exception as e:
            print(f"[SERIAL ERROR] {e}")
            return None

    def get_endstops(self):
        return self.send_command("GET ENDSTOPS")

    def get_beams(self):
        return self.send_command("GET BEAMS")

    def close(self):
        if self.ser:
            self.ser.close()
