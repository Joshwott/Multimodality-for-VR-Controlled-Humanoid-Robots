#Responsible for handling the movement of NAOs arms and joints
from naoqi import ALProxy
from NAOBackend.MetaQuest.vrtrackingserver import ControllerDataServer
import naoconnection, naomovementcontrols
import math, time

CALIBRATED = False
ALPHA = 0.3

calibration = {
    "center": [0, 0, 0],
    "maxX": 0,
    "minX": 0,
    "maxY": 0,
    "minY": 0,
    "maxZ": 0,
    "minZ": 0
}

#Limits can be found here in the NAO Documentation.
#http://doc.aldebaran.com/1-14/family/robots/joints_robot.html.
LEFTARMLIMITS = {
    "ShoulderPitch": (-2.0, 2.0),
    "ShoulderRoll": (0.0, 1.5),
    "ElbowYaw": (-2.0, 2.0),
    "ElbowRoll": (0.1, 1.5)
}

RIGHTARMLIMITS = {
    "ShoulderPitch": (-2.0, 2.0),
    "ShoulderRoll": (-1.5, 0.0),
    "ElbowYaw": (-2.0, 2.0),
    "ElbowRoll": (-1.5, -0.1)
}

LEFTARM = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
RIGHTARM = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]

#Convert the Euler angles from degrees to radians.
#@param angle to convert.
#@return value in radian.
def degreesToRadians(degrees):
    return degrees * math.pi / 180.0

#Implements a clamp to prevent joints from overrotation.
#@param value current value.
#@param minVal minimum value allowed.
#@param maxVal maximum value allowed.
#@return clamped range.
def clamp(value, minVal, maxVal):
    return max(min(value, maxVal), minVal)

#Normalises the values inputted from the raw controller telemetry.
def normalize(value, minVal, maxVal):
    if maxVal - minVal == 0:
        return 0.5
    norm = (value - minVal) / (maxVal - minVal)
    return max(0.0, min(1.0, norm))

#Smooths the movement preventing jittering.
def smooth(new, prev):
    return [ALPHA * n + (1 - ALPHA) * p for n, p in zip(new, prev)]

def separateControllerData(data):
    delimiter = data.split('|')
    leftControllerPosition = delimiter[0]
    rightControllerPosition = delimiter[1]
    leftControllerRotation = delimiter[3]
    rightControllerRotation = delimiter[4]

    leftPosition = list(map(float, leftControllerPosition.split(',')))
    rightPosition = list(map(float, rightControllerPosition.split(',')))
    leftControllerRotation = list(map(float, leftControllerRotation.split(',')))
    rightControllerRotation = list(map(float, rightControllerRotation.split(',')))

    return leftPosition, rightPosition, leftControllerRotation, rightControllerRotation

#Method to get the position of the arm within a 3D space.
#@param current rotation of the arm.
#@param limit of the joint.
#@param arm left or right.
def armPositionFromPosition(position, limit, arm):

    x, y, z = position  # VR coordinates

    xNorm = normalize(x, calibration["minX"], calibration["maxX"])

    if arm == "Right":
        xNorm = 1 - xNorm

    yNorm = normalize(y, calibration["minY"], calibration["maxY"])
    zNorm = normalize(z, calibration["minZ"], calibration["maxZ"])

    shoulderPitch = (1 - yNorm) * (limit["ShoulderPitch"][1] - limit["ShoulderPitch"][0]) + limit["ShoulderPitch"][0]
    shoulderRoll = xNorm * (limit["ShoulderRoll"][1] - limit["ShoulderRoll"][0]) + limit["ShoulderRoll"][0]

    elbowYaw = 0.0
    elbowRoll = 0.5

    return [shoulderPitch, shoulderRoll, elbowYaw, elbowRoll]

motion = ALProxy("ALMotion", naoconnection.getRobotIP(),
                 naoconnection.getRobotPort())

#Calibrates the positions for the user of the robot.
def calibrateNAO():
    global calibration, CALIBRATED

    print("NAO not calibrated yet.")
    print("Calibrating NAO...")
    time.sleep(1)

    print("Hold arms relaxed at your sides...")
    time.sleep(3)
    data = ControllerDataServer.getData()
    leftPos, _, _, _ = separateControllerData(data)
    calibration["center"] = leftPos

    print("Raise arms up...")
    time.sleep(3)
    data = ControllerDataServer.getData()
    leftPos, _, _, _ = separateControllerData(data)
    calibration["maxY"] = leftPos[1]

    print("Push arms down...")
    time.sleep(3)
    data = ControllerDataServer.getData()
    leftPos, _, _, _ = separateControllerData(data)
    calibration["minY"] = leftPos[1]

    print("Stretch arms out sideways...")
    time.sleep(3)
    data = ControllerDataServer.getData()
    leftPos, rightPos, _, _ = separateControllerData(data)
    calibration["maxX"] = max(leftPos[0], rightPos[0])


    print("Bring arms close to body...")
    time.sleep(3)
    data = ControllerDataServer.getData()
    leftPos, rightPos, _, _ = separateControllerData(data)
    calibration["minX"] = min(leftPos[0], rightPos[0])

    print("Reach arms forward...")
    time.sleep(3)
    data = ControllerDataServer.getData()
    leftPos, _, _, _ = separateControllerData(data)
    calibration["maxZ"] = leftPos[2]

    print("Pull arms back...")
    time.sleep(3)
    data = ControllerDataServer.getData()
    leftPos, _, _, _ = separateControllerData(data)
    calibration["minZ"] = leftPos[2]

    CALIBRATED = True
    print("NAO calibrated: ", calibration)

#Runs the arm controls.
def runArmControls():
    prevLeft = [0.0] * 4
    prevRight = [0.0] * 4
    motion.setStiffnesses("Body", 1.0)
    while True:

        if not CALIBRATED:
            calibrateNAO()

        data = ControllerDataServer.getData()
        #print (data)

        if data is None:
            time.sleep(0.01)
            continue

        if naomovementcontrols.isMoving:
            time.sleep(0.02)
            continue

        try:
            leftPos, rightPos, leftRot, rightRot = separateControllerData(data)

            leftAngles = armPositionFromPosition(leftPos, LEFTARMLIMITS, "Left")
            rightAngles = armPositionFromPosition(rightPos, RIGHTARMLIMITS, "Right")

            leftAngles = smooth(leftAngles, prevLeft)
            rightAngles = smooth(rightAngles, prevRight)

            prevLeft = leftAngles
            prevRight = rightAngles

            motion.setAngles(LEFTARM, leftAngles, 0.2)
            motion.setAngles(RIGHTARM, rightAngles, 0.2)

        except Exception as e:
            print("Arm control error:", e)

        time.sleep(0.02)