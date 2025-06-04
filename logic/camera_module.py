import ctypes
import numpy as np
import cv2
import os, sys
import time
import traceback

from hikvision_sdk.MvCameraControl_class import *
from config.config import FRAME_WIDTH, FRAME_HEIGHT, EXPOSURE_TIME, GAIN
from hikvision_sdk.PixelType_header import PixelType_Gvsp_BayerRG8


def enum_cameras():
    try:
        device_list = MV_CC_DEVICE_INFO_LIST()
        tlayer_type = MV_USB_DEVICE
        temp_cam = MvCamera()
        nRet = temp_cam.MV_CC_EnumDevices(tlayer_type, device_list)
        if nRet != 0 or device_list.nDeviceNum == 0:
            print("❌ Geen camera's gevonden")
            return None
        return device_list
    except Exception as e:
        print(f"[FOUT] {e}")
        traceback.print_exc()
        return None

def open_camera(device_info):
    try:
        cam = MvCamera()
        cam.MV_CC_CreateHandle(device_info)
        cam.MV_CC_OpenDevice()
        cam.MV_CC_SetEnumValue("PixelFormat", PixelType_Gvsp_BayerRG8)
        cam.MV_CC_SetIntValue("Width", FRAME_WIDTH)
        cam.MV_CC_SetIntValue("Height", FRAME_HEIGHT)
        cam.MV_CC_SetFloatValue("ExposureTime", EXPOSURE_TIME)
        cam.MV_CC_SetFloatValue("Gain", GAIN)
        cam.MV_CC_SetEnumValue("TriggerMode", 0)  # Continuous mode
        cam.MV_CC_StartGrabbing()
        return cam
    except Exception as e:
        print(f"[FOUT BIJ CAMERA OPENEN] {e}")
        traceback.print_exc()
        return None
