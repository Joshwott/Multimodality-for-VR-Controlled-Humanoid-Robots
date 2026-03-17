import openvr

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