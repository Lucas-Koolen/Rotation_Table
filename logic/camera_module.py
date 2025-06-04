import cv2
import numpy as np
from hikvision_sdk.MvCameraControl_class import *
from config.config import (
    FRAME_WIDTH,
    FRAME_HEIGHT,
    PIXEL_FORMAT,
    EXPOSURE_TIME,
    GAIN,
    MM_PER_PIXEL,
)
from sensor.height_sensor import HeightSensorReader


def init_camera():
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0 or deviceList.nDeviceNum == 0:
        print("[CAMERA] Geen camera gevonden.")
        return None

    # Print info about all detected cameras to aid troubleshooting
    for i in range(deviceList.nDeviceNum):
        dev_info = deviceList.pDeviceInfo[i].contents
        if dev_info.nTLayerType == MV_GIGE_DEVICE:
            info = dev_info.SpecialInfo.stGigEInfo
        else:
            info = dev_info.SpecialInfo.stUsb3VInfo

        model = bytes(info.chModelName).split(b"\x00", 1)[0].decode(errors="ignore")
        serial = bytes(info.chSerialNumber).split(b"\x00", 1)[0].decode(errors="ignore")
        version = bytes(info.chDeviceVersion).split(b"\x00", 1)[0].decode(errors="ignore")
        print(f"[CAMERA] Device {i}: {model} SN={serial} Version={version}")

    cam = MvCamera()
    cam.MV_CC_CreateHandle(deviceList.pDeviceInfo[0])
    cam.MV_CC_OpenDevice()
    cam.MV_CC_SetEnumValue("PixelFormat", PIXEL_FORMAT)
    cam.MV_CC_SetIntValue("Width", FRAME_WIDTH)
    cam.MV_CC_SetIntValue("Height", FRAME_HEIGHT)
    cam.MV_CC_SetFloatValue("ExposureTime", EXPOSURE_TIME)
    cam.MV_CC_SetFloatValue("Gain", GAIN)
    cam.MV_CC_StartGrabbing()
    return cam


def get_frame_tuple(cam, timeout=2000):
    """Retrieve a single frame from ``cam`` using the Hikvision SDK.

    Parameters
    ----------
    cam : ``MvCamera``
        Open camera handle.
    timeout : int, optional
        Timeout in milliseconds, by default ``2000``.

    Returns
    -------
    tuple
        ``(ret, data_buf, frame_info)`` where ``ret`` is the SDK return code and
        ``data_buf`` is a ``bytes`` object with the raw image. ``frame_info`` is
        the filled ``MV_FRAME_OUT_INFO_EX`` structure. If grabbing fails,
        ``data_buf`` and ``frame_info`` are ``None``.
    """

    n_data_size = FRAME_WIDTH * FRAME_HEIGHT * 3
    data_buf = (c_ubyte * n_data_size)()
    frame_info = MV_FRAME_OUT_INFO_EX()

    ret = cam.MV_CC_GetOneFrameTimeout(data_buf, n_data_size, frame_info, timeout)
    if ret != 0:
        return ret, None, None

    # Convert to bytes to decouple from the underlying buffer
    return ret, bytes(data_buf[: frame_info.nFrameLen]), frame_info


def capture_frame(cam):
    """Return the next frame from ``cam`` as an OpenCV ``numpy`` array."""

    ret, data_buf, frame_info = get_frame_tuple(cam)
    if ret != 0 or data_buf is None:
        return None

    frame = np.frombuffer(data_buf, dtype=np.uint8)
    frame = frame.reshape((frame_info.nHeight, frame_info.nWidth, 3))
    return frame.copy()


def convert_frame_to_opencv(frame_tuple):
    """Converts the raw tuple returned by ``MV_CC_GetOneFrameTimeout`` to an
    OpenCV compatible ``numpy`` array.

    Parameters
    ----------
    frame_tuple : tuple or ``numpy`` array
        Data returned by ``MvCamera.MV_CC_GetOneFrameTimeout``.  Some parts of
        the code call the SDK method directly which yields ``(ret, data_buf,
        frame_info)``.  When the frame is already a ``numpy`` array the value is
        returned unchanged.

    Returns
    -------
    ``numpy.ndarray`` or ``None``
        BGR image or ``None`` when conversion fails.
    """

    # If the given value already looks like an OpenCV image, return it
    if isinstance(frame_tuple, np.ndarray):
        return frame_tuple

    if not isinstance(frame_tuple, tuple) or len(frame_tuple) != 3:
        return None

    _, data_buf, stFrameInfo = frame_tuple

    if data_buf is None or stFrameInfo is None:
        return None

    try:
        frame = np.frombuffer(data_buf, dtype=np.uint8)
        frame = frame.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth, 3))
        return frame.copy()
    except Exception:
        return None


def detect_box_dimensions(frame, height_reader: HeightSensorReader):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_cnt = max(contours, key=cv2.contourArea, default=None)
    if best_cnt is None:
        return None

    rect = cv2.minAreaRect(best_cnt)
    (x, y), (w, h), angle = rect
    length_mm = max(w, h) * MM_PER_PIXEL
    width_mm = min(w, h) * MM_PER_PIXEL
    height_mm = height_reader.get_distance()

    return {
        "length": round(length_mm, 1),
        "width": round(width_mm, 1),
        "height": round(height_mm, 1) if height_mm else None,
    }
