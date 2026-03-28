# Main file responsible for initiating all the code.
import threading
from NAOBackend.MetaQuest.vrtrackingserver import ControllerDataServer
from NAORobot import naomovementcontrols, naoarmtracking

# Main method starts the Meta Quest 2 and NAO robot links
def main():
    # Start UDP server in a background threadq
    serverThread = threading.Thread(target=ControllerDataServer.startServer)
    serverThread.daemon = True
    serverThread.start()

    movementThread = threading.Thread(target=naomovementcontrols.runMovementControls)
    movementThread.daemon = True
    movementThread.start()

    armThread = threading.Thread(target=naoarmtracking.runArmControls)
    armThread.daemon = True
    armThread.start()

    print("All Daemons alive...")
    while True:
        pass


if __name__ == "__main__":
    main()