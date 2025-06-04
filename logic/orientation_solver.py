def solve_orientation(measured_dims, matched_dims, shape):
    """
    Bepaal benodigde rotatie en flip om gemeten doos gelijk te maken aan de matched orientatie.
    """
    mL, mW, mH = measured_dims['length'], measured_dims['width'], measured_dims['height']
    dL, dW, dH = matched_dims['length'], matched_dims['width'], matched_dims['height']

    rotatie = 0
    flip = "none"
    uitleg = []

    # Stap 1: check of lengte en breedte verwisseld moeten worden
    if abs(mL - dW) < abs(mL - dL):
        rotatie = 90
        uitleg.append("L/B verwisseld → 90° draaien")
    elif abs(mL - dL) < 1e-2 and abs(mW - dW) < 1e-2:
        rotatie = 0
        uitleg.append("L/B komt overeen → geen draai nodig")
    else:
        rotatie = 180
        uitleg.append("L/B wijken af → 180° draaien")

    # Stap 2: fliplogica enkel voor cilinders of als hoogte totaal niet overeenkomt
    if shape == "cylinder":
        if abs(mH - dH) > 1e-2:
            flip = "L1L2"
            uitleg.append("Cilinder met verkeerde hoogte → 180° flip")
        else:
            uitleg.append("Cilinder in juiste hoogte → geen flip")
    else:
        uitleg.append("Box → geen flip nodig")

    return {
        "rotation_angle": rotatie,
        "flip": flip,
        "info": " | ".join(uitleg)
    }
