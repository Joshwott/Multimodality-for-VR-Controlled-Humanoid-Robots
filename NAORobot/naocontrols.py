from naoqi import ALProxy
from MetaQuest.vrtrackingserver import ControllerDataServer
import naoconnection
import time

motion = ALProxy("ALMotion", naoconnection.getRobotIP(),
              naoconnection.getRobotPort())
motion.wakeUp()


def controlArm(data):
    print(data)

def runControls():
    while True:
        with ControllerDataServer.lock:
            data = ControllerDataServer.controllerData

        if data is not None:
            print(data)
        time.sleep(5)