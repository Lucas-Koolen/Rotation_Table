import cv2
import numpy as np
from config.config import FRAME_WIDTH, FRAME_HEIGHT, MM_PER_PIXEL
from hikvision_sdk.MvCameraControl_class import MV_FRAME_OUT_INFO_EX

def convert_frame_to_opencv(data_buf):
    img = np.frombuffer(data_buf, dtype=np.uint8).reshape((FRAME_HEIGHT, FRAME_WIDTH))
    return cv2.cvtColor(img, cv2.COLOR_BAYER_RG2BGR)

def get_frame_tuple(camera):
    try:
        data_buf = bytearray(FRAME_WIDTH * FRAME_HEIGHT)
        st_param = MV_FRAME_OUT_INFO_EX()
        ret = camera.MV_CC_GetOneFrameTimeout(data_buf, FRAME_WIDTH * FRAME_HEIGHT, st_param, 1000)
        if ret != 0:
            return None, None
        frame = convert_frame_to_opencv(data_buf)
        return frame, data_buf
    except:
        return None, None

def detect_box_dimensions(image, mm_per_pixel=MM_PER_PIXEL):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        x, y, w, h = cv2.boundingRect(contours[0])
        return round(w * mm_per_pixel, 2), round(h * mm_per_pixel, 2)
    return 0, 0
