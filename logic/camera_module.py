import ctypes
import numpy as np
import cv2
import os, sys
import time
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "hikvision_sdk")))
from MvCameraControl_class import *
from config.config import *

def enum_cameras():
    try:
        device_list = MV_CC_DEVICE_INFO_LIST()
        tlayer_type = MV_USB_DEVICE
        temp_cam = MvCamera()
        nRet = temp_cam.MV_CC_EnumDevices(tlayer_type, device_list)
        if nRet != 0 or device_list.nDeviceNum == 0:
            print("❌ Geen camera's gevonden")
            return None

        print(f"✅ {device_list.nDeviceNum} camera('s) gevonden:")
        for i in range(device_list.nDeviceNum):
            dev = device_list.pDeviceInfo[i].contents
            if dev.nTLayerType == MV_USB_DEVICE:
                model = bytes(dev.SpecialInfo.stUsb3VInfo.chModelName).decode('utf-8').strip('\x00')
                serial = bytes(dev.SpecialInfo.stUsb3VInfo.chSerialNumber).decode('utf-8').strip('\x00')
                print(f"  🔍 USB: {model} | SN: {serial}")
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

def grab_frame(cam):
    try:
        data_buf = bytearray(FRAME_WIDTH * FRAME_HEIGHT)
        st_param = MV_FRAME_OUT_INFO_EX()
        ret = cam.MV_CC_GetOneFrameTimeout(data_buf, FRAME_WIDTH * FRAME_HEIGHT, st_param, 1000)
        if ret != 0:
            print("[FOUT] Geen frame ontvangen.")
            return None

        img = np.frombuffer(data_buf, dtype=np.uint8).reshape((FRAME_HEIGHT, FRAME_WIDTH))
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BAYER_RG2BGR)
        return img_rgb
    except Exception as e:
        print(f"[FOUT BIJ FRAME OPHALEN] {e}")
        traceback.print_exc()
        return None
