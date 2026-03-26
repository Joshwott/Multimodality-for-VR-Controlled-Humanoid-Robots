from naoqi import ALProxy
from NAOBackend.MetaQuest.vrtrackingserver import ControllerDataServer
import naoconnection
import keyboard, time

JOYSTICKDEADZONE = 0.4

motion = ALProxy("ALMotion", naoconnection.getRobotIP(),
                 naoconnection.getRobotPort())

posture = ALProxy("ALRobotPosture", naoconnection.getRobotIP(),
                  naoconnection.getRobotPort())

motion.wakeUp()
posture.goToPosture("StandInit", 0.5)

def separateControllerData(data):

    delimiter = data.split('|')
    joystickPosition = delimiter[2]
    xPos, yPos = joystickPosition.split(',')

    x = float(xPos)
    y = float(yPos)

    return x, y

def runMovementControls():
    posture.goToPosture("StandInit", 0.5)

    while True:

        data = ControllerDataServer.getData()

        print(data)

        if data is None:
            motion.stopMove()
            time.sleep(0.01)
            continue

        joystickX, joystickY = separateControllerData(data)

        if abs(joystickX) < JOYSTICKDEADZONE:
            joystickX = 0.0
        if abs(joystickY) < JOYSTICKDEADZONE:
            joystickY = 0.0

        forward = joystickY * 0.1
        rotation = joystickX * 0.3

        if forward != 0.0 or rotation != 0.0:
            motion.move(forward, 0, rotation)
        else:
            motion.stopMove()

        if keyboard.is_pressed('q'):
            print("quit")
            break

        time.sleep(0.01)

    motion.stopMove()
    motion.rest()
