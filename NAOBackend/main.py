# Main file responsible for initiating all the code.
import threading
from NAOBackend.MetaQuest.vrtrackingserver import ControllerDataServer
from NAORobot import naomovementcontrols, naobodytracking, naocamera
import time

# Main method starts the Meta Quest 2 and NAO robot links
def main():
    # Start UDP server in a background threadq
    serverThread = threading.Thread(target=ControllerDataServer.startServer)
    serverThread.daemon = True
    serverThread.start()

    movementThread = threading.Thread(target=naomovementcontrols.runMovementControls)
    movementThread.daemon = True
    movementThread.start()

    armThread = threading.Thread(target=naobodytracking.runArmTracking)
    armThread.daemon = True
    armThread.start()

    headThread = threading.Thread(target=naobodytracking.runHeadTracking)
    headThread.daemon = True
    headThread.start()

    time.sleep(10)

    cameraThread = threading.Thread(target=naocamera.startCameraClient)
    cameraThread.daemon = True
    cameraThread.start()

    print("All Daemon threads alive...")
    while True:
        pass


if __name__ == "__main__":
    main()