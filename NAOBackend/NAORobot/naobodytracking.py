#Responsible for handling the movement of NAOs arms and joints
from naoqi import ALProxy

from NAOBackend.MetaQuest import vrtrackingserver
from NAOBackend.MetaQuest.vrtrackingserver import ControllerDataServer
from NAOBackend.Webots.webotserver import sendJointData
import naoconnection, naomovementcontrols
import math, time, socket, keyboard

CALIBRATED = False
ALPHA = 0.3

calibration = {
    "center": [0, 0, 0],
    "maxXLeft": 0,
    "maxXRight": 0,
    "minXLeft": 0,
    "minXRight": 0,
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

HEADLIMITS = {
    "HeadPitch": (-2.0, 2.0),
    "HeadYaw": (-0.6, 0.5)
}

LEFTARM = ["LShoulderPitch", "LShoulderRoll", "LElbowYaw", "LElbowRoll"]
RIGHTARM = ["RShoulderPitch", "RShoulderRoll", "RElbowYaw", "RElbowRoll"]
HEAD = ["HeadPitch", "HeadYaw"]

motion = ALProxy("ALMotion", naoconnection.getRobotIP(),
                 naoconnection.getRobotPort())

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
#@param value current position.
#@param minVal minimum allowed value.
#@param maxVal maximum allowed value.
#@return normalised value
def normalise(value, minVal, maxVal):
    if maxVal - minVal == 0:
        return 0.5
    norm = (value - minVal) / (maxVal - minVal)
    return max(0.0, min(1.0, norm))

#Smooths the movement preventing jittering.
def smooth(new, prev):
    return [ALPHA * n + (1 - ALPHA) * p for n, p in zip(new, prev)]

#Separates the controller data sent from to the UDP Server using the delimiter
#@param data set from VR Headset.
#@return positions of the controllers and head
def separateControllerData(data):
    delimiter = data.split('|')
    leftControllerPosition = delimiter[0]
    rightControllerPosition = delimiter[1]
    leftControllerRotation = delimiter[3]
    rightControllerRotation = delimiter[4]
    headPosition = delimiter[5]
    headRotation = delimiter[6]

    leftPosition = list(map(float, leftControllerPosition.split(',')))
    rightPosition = list(map(float, rightControllerPosition.split(',')))
    leftRotation = list(map(float, leftControllerRotation.split(',')))
    rightRotation = list(map(float, rightControllerRotation.split(',')))
    headPos = list(map(float, headPosition.split(',')))
    headRot = list(map(float, headRotation.split(',')))


    return leftPosition, rightPosition, leftControllerRotation, rightControllerRotation, headRot

def headRotationFromHeadset(rotation):

    pitch, yaw, roll = rotation
    pitch = degreesToRadians(pitch)
    yaw = degreesToRadians(yaw)

    if pitch > math.pi:
        pitch -= 2 * math.pi
    if yaw > math.pi:
        yaw -= 2 * math.pi

    headYaw = clamp(yaw, *HEADLIMITS["HeadYaw"])
    headPitch = clamp(pitch, *HEADLIMITS["HeadPitch"])

    return [headPitch, headYaw]


#Method to get the position of the arm within a 3D space.
#@param current rotation of the arm.
#@param limit of the joint.
#@param arm left or right.
def armPositionFromControllerPosition(position, limit, arm):
    x, y, z = position  # VR coordinates

    if arm == "Right":
        xNorm = normalise(x, calibration["minXRight"], calibration["maxXRight"])
        xNorm = 1 - xNorm
    else:
        xNorm = normalise(x, calibration["minXLeft"], calibration["maxXLeft"])


    yNorm = normalise(y, calibration["minY"], calibration["maxY"])
    zNorm = normalise(z, calibration["minZ"], calibration["maxZ"])
    shoulderPitch = (1 - yNorm) * (limit["ShoulderPitch"][1] - limit["ShoulderPitch"][0]) + limit["ShoulderPitch"][0]

    shoulderRoll = xNorm * (limit["ShoulderRoll"][1] - limit["ShoulderRoll"][0]) + limit["ShoulderRoll"][0]
    elbowYaw = 0.0
    elbowRoll = 0.5

    return [shoulderPitch, shoulderRoll, elbowYaw, elbowRoll]

#Calibrates the positions for the user of the robot.
def calibrateNAO():
    global calibration, CALIBRATED

    print("NAO Arms not calibrated yet.")
    print("Calibrating Arms...")
    time.sleep(1)

    def waitForData():
        data = None
        while data is None:
            data = ControllerDataServer.getData()
            time.sleep(0.01)
        return data

    print("Hold arms relaxed at your sides...")
    time.sleep(3)
    data = waitForData()
    leftPos, rightPos, _, _, _ = separateControllerData(data)
    calibration["center"] = leftPos
    calibration["minXLeft"] = leftPos[0]
    calibration["minXRight"] = rightPos[0]

    print("Raise arms up...")
    time.sleep(3)
    data = waitForData()
    leftPos, _, _, _, _ = separateControllerData(data)
    calibration["maxY"] = leftPos[1]

    print("Push arms down...")
    time.sleep(3)
    data = waitForData()
    leftPos, _, _, _, _ = separateControllerData(data)
    calibration["minY"] = leftPos[1]

    print("Stretch arms out sideways...")
    time.sleep(3)
    data = waitForData()
    leftPos, rightPos, _, _, _ = separateControllerData(data)
    calibration["maxXLeft"] = leftPos[0]
    calibration["maxXRight"] = rightPos[0]

    print("Reach arms forward...")
    time.sleep(3)
    data = waitForData()
    leftPos, _, _, _, _ = separateControllerData(data)
    calibration["maxZ"] = leftPos[2]

    print("Pull arms back...")
    time.sleep(3)
    data = waitForData()
    leftPos, _, _, _, _ = separateControllerData(data)
    calibration["minZ"] = leftPos[2]

    CALIBRATED = True
    print("NAO calibrated: ", calibration)

#Runs the arm controls.
def runArmTracking():
    prevLeft = [0.0] * 4
    prevRight = [0.0] * 4
    motion.setStiffnesses("Body", 1.0)
    while True:

        if not CALIBRATED:
            calibrateNAO()
            sendCalibrationData()

        data = ControllerDataServer.getData()

        if data is None:
            time.sleep(0.01)
            continue

        if naomovementcontrols.isMoving:
            time.sleep(0.02)
            continue

        try:
            leftPos, rightPos, leftRot, rightRot, _ = separateControllerData(data)
            leftAngles = armPositionFromControllerPosition(leftPos, LEFTARMLIMITS, "Left")
            rightAngles = armPositionFromControllerPosition(rightPos, RIGHTARMLIMITS, "Right")
            leftAngles = smooth(leftAngles, prevLeft)
            rightAngles = smooth(rightAngles, prevRight)
            prevLeft = leftAngles
            prevRight = rightAngles
            motion.setAngles(LEFTARM, leftAngles, 0.2)
            motion.setAngles(RIGHTARM, rightAngles, 0.2)
            sendJointData(LEFTARM, leftAngles)
            sendJointData(RIGHTARM, rightAngles)

        except Exception as e:
            print("Arm control error:", e)

        if keyboard.is_pressed('q'):
            printControllerPosition()

        time.sleep(0.02)

#Sends the calibrated data to the Quest headset to be used as boundries in the haptic feedback.
def sendCalibrationData():

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    payload = "CalibrationData|" + ",".join([
        str(calibration["minXLeft"]),
        str(calibration["maxXLeft"]),
        str(calibration["minXRight"]),
        str(calibration["maxXRight"]),
        str(calibration["minY"]),
        str(calibration["maxY"]),
        str(calibration["minZ"]),
        str(calibration["maxZ"]),
    ])

    questIP = "10.138.161.15"
    questPort = 5010
    sock.sendto(payload.encode(), (questIP, questPort))

    print("Calibration data: " + payload + " sent to Meta Quest 2...")


def runHeadTracking():
    prevHead = [0.0, 0.0]
    motion.setStiffnesses("Head", 1.0)
    while True:

        data = ControllerDataServer.getData()

        if data is None:
            time.sleep(0.01)
            continue

        if naomovementcontrols.isMoving:
            time.sleep(0.02)
            continue

        try:
            _, _, _, _, headRot = separateControllerData(data)
            headAngles = headRotationFromHeadset(headRot)
            headAngles = smooth(headAngles, prevHead)
            prevHead = headAngles
            motion.setAngles(HEAD, headAngles, 0.2)
            sendJointData(HEAD, headAngles)

        except Exception as e:
            print("Head control error:", e)

        time.sleep(0.02)

def printControllerPosition():
    print(ControllerDataServer.getData())