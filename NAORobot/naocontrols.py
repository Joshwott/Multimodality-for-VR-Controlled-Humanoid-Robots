from naoqi import ALProxy
from MetaQuest.vrtrackingserver import ControllerDataServer
import naoconnection
import time
import math

motion = ALProxy("ALMotion", naoconnection.getRobotIP(),
              naoconnection.getRobotPort())

posture = ALProxy("ALRobotPosture", naoconnection.getRobotIP(),
                  naoconnection.getRobotPort())

motion.wakeUp()
motion.setStiffnesses("Body", 1.0)

'''
def controlArms(data):
    print("Arm Found")

    try:
        position = getArmPosition(data)
        rotation = getArmRotation(data)

        x = position[0]
        y = -position[1]
        z = position[2]

        scale = 0.4
        x = x * scale
        y = y * scale
        z = z * scale

        def clamp(val, min_val, max_val):
            return max(min(val, max_val), min_val)

        x = clamp(x, 0.05, 0.4)
        y = clamp(y, -0.3, 0.3)
        z = clamp(z, 0.05, 0.5)

        qx = rotation[0]
        qy = rotation[1]
        qz = rotation[2]
        qw = rotation[3]

        wx, wy, wz = quat_to_axis_angle(qx, qy, qz, qw)

        pos6D = [x, y, z, wx, wy, wz]

        arm = "RArm" if data['controller'] == "Right" else "LArm"

        motion.setPosition(arm, 0, pos6D, 0.2, 7)

        print("Moving", arm, pos6D)

    except Exception, e:
        print("Error in Control", e)


def quat_to_axis_angle(qx, qy, qz, qw):
    angle = 2 * math.acos(qw)

    s = math.sqrt(1 - qw * qw)
    if s < 0.001:
        x, y, z = qx, qy, qz
    else:
        x = qx / s
        y = qy / s
        z = qz / s

    return [x * angle, y * angle, z * angle]

def getArmPosition(data):
    x, y, z = data['position']
    return x, y, z

def getArmRotation(data):
    qx, qy, qz, qw = data['orientation']
    return qx, qy, qz, qw

'''

def runControls():
    while True:
        with ControllerDataServer.lock:
            data = ControllerDataServer.controllerData

        if data is not None:
            if data['controller'] == "Right" or data['controller'] == "Left":
                #controlArms(data)
                motion.setAngles(
                    ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll", "RWristYaw"],
                    [-1.0, -0.8, 1.5, 0.5, 0.0],
                    0.2
                )

        time.sleep(5)
