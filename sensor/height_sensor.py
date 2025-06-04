import serial
import threading
from config.config import SERIAL_PORT, BAUD_RATE

class HeightSensorReader:
    def __init__(self):
        self.distance = None
        self.running = True

        try:
            self.ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        except Exception as e:
            print(f"[HEIGHT SENSOR] Fout bij openen COM-poort: {e}")
            self.ser = None
            self.running = False

        if self.ser:
            self.thread = threading.Thread(target=self._read_loop, daemon=True)
            self.thread.start()

    def _read_loop(self):
        while self.running:
            try:
                line = self.ser.readline().decode().strip()
                if line.startswith("HEIGHT:"):
                    val = line.split(":")[1]
                    self.distance = float(val)
            except Exception:
                continue

    def get_distance(self):
        return self.distance

    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()
