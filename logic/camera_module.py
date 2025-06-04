import cv2
import numpy as np
from hikvision_sdk.MvCameraControl_class import *
from config.config import FRAME_WIDTH, FRAME_HEIGHT, PIXEL_FORMAT, EXPOSURE_TIME, GAIN, MM_PER_PIXEL
from sensor.height_sensor import HeightSensorReader

def init_camera():
    deviceList = MV_CC_DEVICE_INFO_LIST()
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
    if ret != 0 or deviceList.nDeviceNum == 0:
        print("[CAMERA] Geen camera gevonden.")
        return None

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

def capture_frame(cam):
    data_buf = None
    stFrameInfo = MV_FRAME_OUT_INFO_EX()
    ret, data_buf, stFrameInfo = cam.MV_CC_GetOneFrameTimeout(2000)

    if ret != 0 or data_buf is None:
        return None

    frame = np.frombuffer(data_buf, dtype=np.uint8)
    frame = frame.reshape((stFrameInfo.nHeight, stFrameInfo.nWidth, 3))
    return frame.copy()

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
        "height": round(height_mm, 1) if height_mm else None
    }
