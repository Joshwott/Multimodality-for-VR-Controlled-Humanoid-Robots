import openvr
import time

def get_device_class(device_class):
    if device_class == openvr.TrackedDeviceClass_HMD:
        return "Headset"
    elif device_class == openvr.TrackedDeviceClass_Controller:
        return "Controller"
    elif device_class == openvr.TrackedDeviceClass_TrackingReference:
        return "Base Station"
    elif device_class == openvr.TrackedDeviceClass_GenericTracker:
        return "Tracker"
    else:
        return "Unknown"

def get_position(pose):
    matrix = pose.mDeviceToAbsoluteTracking
    return matrix[0][3], matrix[1][3], matrix[2][3]


def start_tracking():
    try:
        vr_system = openvr.init(openvr.VRApplication_Scene)
        while True:

            poses = vr_system.getDeviceToAbsoluteTrackingPose(openvr.TrackingUniverseStanding, 0,
                                                              openvr.k_unMaxTrackedDeviceCount)

            for i in range(openvr.k_unMaxTrackedDeviceCount):

                if not vr_system.isTrackedDeviceConnected(i):
                    continue

                device_class = vr_system.getTrackedDeviceClass(i)

                if device_class != vr_system.getTrackedDeviceClass(i):
                    continue

                pose = poses[i]

                if not pose.bPoseIsValid:
                    continue

                position = get_position(pose)
                print("Device ID:", i)
                print("Position (X, Y, Z:", position)
                print("----------------------")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopped tracking.")

    except openvr.OpenVRError as e:
        print("SteamVR error:", e)

    finally:
        openvr.shutdown()
