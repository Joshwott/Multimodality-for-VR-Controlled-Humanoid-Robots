# Main file responsible for initiating all the code.
import threading
import time
from NAOBackend.MetaQuest.vrtrackingserver import ControllerDataServer
from NAORobot import naomovementcontrols

# Main method starts the Meta Quest 2 and NAO robot links
def main():
    # Start UDP server in a background threadq
    serverThread = threading.Thread(target=ControllerDataServer.startServer)
    serverThread.daemon = True
    serverThread.start()



    naocontrols.runMovementControls()


if __name__ == "__main__":
    main()