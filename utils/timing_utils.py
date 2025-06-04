import time

def millis():
    return int(time.time() * 1000)

class Timer:
    def __init__(self, interval_ms):
        self.interval = interval_ms
        self.last_time = millis()

    def ready(self):
        current = millis()
        if current - self.last_time >= self.interval:
            self.last_time = current
            return True
        return False
