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


def send_rotation_command(angle, flip="none"):
    """Stuur een rotatiecommando naar de Arduino.

    Parameters
    ----------
    angle : float or int
        Hoek in graden voor servo-kanaal 0.
    flip : str, optional
        Type flip, standaard ``"none"``. Wordt alleen gelogd.
    """

    arduino = ArduinoComm()
    if not arduino.ser:
        return None

    response = arduino.send_command(f"ROTATE 0 {int(angle)}")

    if flip and flip.lower() != "none":
        arduino.send_command(f"# Flip not supported: {flip}")

    arduino.close()
    return response
