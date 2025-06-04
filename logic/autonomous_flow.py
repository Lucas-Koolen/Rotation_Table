from logic.camera_module import (
    detect_box_dimensions,
    convert_frame_to_opencv,
    get_frame_tuple,
)
from logic.box_identifier import identify_box
from logic.orientation_solver import solve_orientation
from arduino_comm.arduino_comm import send_rotation_command

# Wordt ingesteld vanuit main
CAMERA = None
HEIGHT_READER = None

def run_autonomous_cycle():
    from ui.dashboard import update_dashboard_status
    print("=== ROTATION SYSTEM: AUTONOME CYCLE START ===")
    update_dashboard_status("Wachten op boxdetectie...")

    if CAMERA is None:
        update_dashboard_status("Camera niet geïnitialiseerd.")
        print("[FLOW] Camera ontbreekt")
        return

    if HEIGHT_READER is None:
        update_dashboard_status("Hoogtesensor niet geïnitialiseerd.")
        print("[FLOW] Hoogtesensor ontbreekt")
        return

    frame_tuple = get_frame_tuple(CAMERA)
    if not frame_tuple or frame_tuple[1] is None:
        update_dashboard_status("Geen cameraframe ontvangen.")
        return

    frame = convert_frame_to_opencv(frame_tuple)
    if frame is None:
        update_dashboard_status("Ongeldig cameraframe.")
        return

    dims = detect_box_dimensions(frame, HEIGHT_READER)
    if dims is None or dims["height"] is None:
        update_dashboard_status("Geen box gedetecteerd.")
        return

    print(f"[FLOW] Gedetecteerd: {dims['length']} x {dims['width']} x {dims['height']} mm")

    box_info = identify_box(dims["length"], dims["width"], dims["height"])
    common_id = box_info["common_id"]
    shape = box_info["shape"]
    deviation = box_info["deviation"]
    match_score = box_info["match_score"]

    print(f"[FLOW] Match: commonId={common_id}, shape={shape}")
    print(f"[FLOW] Afwijking: {deviation}")
    print(f"[FLOW] Match Score: {match_score:.4f}" if match_score else "[FLOW] Geen match score")

    update_dashboard_status(f"Match gevonden:\nCommonId={common_id}\n{dims['length']}x{dims['width']}x{dims['height']} mm")

    # Bepaal benodigde rotatie
    orientation = solve_orientation(dims, box_info["matched_dims"], shape)
    rotation = orientation["rotation_angle"]
    flip = orientation["flip"]
    uitleg = orientation["info"]
    print(f"[FLOW] Rotatie nodig: {rotation}°, Flip: {flip}")
    print(f"[FLOW] Uitleg: {uitleg}")

    # Stuur commando naar Arduino
    send_rotation_command(rotation, flip)

    print("=== EINDE CYCLE ===")
