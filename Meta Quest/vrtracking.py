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


'''
try:
    vr_system = openvr.init(openvr.VRApplication_Scene)

    print("Scanning for connected VR devices...\n")

    for device_index in range(openvr.k_unMaxTrackedDeviceCount):

        if not vr_system.isTrackedDeviceConnected(device_index):
            continue

        device_class = vr_system.getTrackedDeviceClass(device_index)
        device_type = get_device_class(device_class)

        model = vr_system.getStringTrackedDeviceProperty(
            device_index,
            openvr.Prop_ModelNumber_String
        )

        print("Device ID:", device_index)
        print("Type:", device_type)
        print("Model:", model)
        print("----------------------")

    openvr.shutdown()

except openvr.OpenVRError as e:
    print("SteamVR not detected or headset not connected.")
    print(e)
'''