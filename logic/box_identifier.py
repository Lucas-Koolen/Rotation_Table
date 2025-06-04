from database.sql_interface import get_all_boxes
from config.config import MATCH_TOLERANCE_LB, MATCH_TOLERANCE_H, WEIGHTS

def identify_box(measured_length, measured_width, measured_height):
    # Herken vorm op basis van verhouding lengte/breedte
    ratio = max(measured_length, measured_width) / min(measured_length, measured_width)
    shape = 'cylinder' if ratio <= 1.15 else 'box'

    candidates = get_all_boxes()
    best_match = None
    best_score = float('inf')

    # Test beide oriëntaties: (L,W) en (W,L)
    orientations = [
        (measured_length, measured_width),
        (measured_width, measured_length)
    ]

    for (meas_L, meas_W) in orientations:
        for entry in candidates:
            if entry['shape'] != shape:
                continue

            # Conversie naar float om TypeError met Decimal te vermijden
            db_L = float(entry['length'])
            db_W = float(entry['width'])
            db_H = float(entry['height'])

            dev_L = abs(meas_L - db_L) / db_L
            dev_W = abs(meas_W - db_W) / db_W
            dev_H = abs(measured_height - db_H) / db_H

            # Check tolerantiegrens op L en B (H is niet leidend)
            if dev_L > MATCH_TOLERANCE_LB or dev_W > MATCH_TOLERANCE_LB:
                continue

            score = (dev_L * WEIGHTS['length'] +
                     dev_W * WEIGHTS['width'] +
                     dev_H * WEIGHTS['height'])

            if score < best_score:
                best_score = score
                best_match = {
                    'commonId': entry['commonId'],
                    'shape': shape,
                    'matched_dims': {'length': db_L, 'width': db_W, 'height': db_H},
                    'measured_dims': {'length': meas_L, 'width': meas_W, 'height': measured_height},
                    'deviation': {'length': dev_L, 'width': dev_W, 'height': dev_H},
                    'match_score': round(score, 4)
                }

    return best_match if best_match else {
        'commonId': None,
        'shape': shape,
        'matched_dims': None,
        'measured_dims': {'length': measured_length, 'width': measured_width, 'height': measured_height},
        'deviation': None,
        'match_score': None
    }
