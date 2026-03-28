#Responsible for controlling the movement of the NAO robot using the ALProxy and Controller Telemetry.
from naoqi import ALProxy
from NAOBackend.MetaQuest.vrtrackingserver import ControllerDataServer
import naoconnection
import keyboard, time

isMoving = False
DRIFTBUFFER = 0.4

motion = ALProxy("ALMotion", naoconnection.getRobotIP(),
                 naoconnection.getRobotPort())

posture = ALProxy("ALRobotPosture", naoconnection.getRobotIP(),
                  naoconnection.getRobotPort())

motion.wakeUp()
posture.goToPosture("StandInit", 0.5)

#Separates the joystick data received from the Quest-Python UDP Server.
#@params data received from controllers.
#@return x, y coordinates of the joystick.
def separateJoystickData(data):
    delimiter = data.split('|')
    joystickPosition = delimiter[2]
    xPos, yPos = joystickPosition.split(',')

    x = float(xPos)
    y = float(yPos)

    return x, y

#Runs and moves the position of the NAO robot based on joystick position.
def runMovementControls():
    global isMoving

    posture.goToPosture("StandInit", 0.5)

    while True:
        data = ControllerDataServer.getData()

        if data is None:
            motion.stopMove()
            time.sleep(0.01)
            continue

        joystickX, joystickY = separateJoystickData(data)
        if abs(joystickX) < DRIFTBUFFER:
            joystickX = 0.0
        if abs(joystickY) < DRIFTBUFFER:
            joystickY = 0.0

        forward = joystickY * 0.1
        rotation = -joystickX * 0.3
        if forward != 0.0 or rotation != 0.0:
            isMoving = True
            motion.move(forward, 0, rotation)
        else:
            isMoving = False
            motion.stopMove()

        if keyboard.is_pressed('q'):
            print("quit")
            break

        time.sleep(0.01)

    motion.stopMove()
    motion.rest()
