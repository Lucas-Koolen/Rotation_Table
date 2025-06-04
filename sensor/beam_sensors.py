from arduino_comm.arduino_comm import ArduinoComm

def parse_beams(response):
    # Voorbeeld response: "b10 b21"
    status = {'L1': None, 'L2': None}
    parts = response.split()
    for part in parts:
        if part.startswith("b10"):
            status['L1'] = False
        elif part.startswith("b11"):
            status['L1'] = True
        elif part.startswith("b20"):
            status['L2'] = False
        elif part.startswith("b21"):
            status['L2'] = True
    return status

def get_beam_status():
    arduino = ArduinoComm()
    response = arduino.get_beams()
    return parse_beams(response) if response else None
