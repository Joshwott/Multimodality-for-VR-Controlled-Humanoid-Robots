# Main file responsible for initiating all the code.
import threading
from MetaQuest import vrtrackingserver
from NAORobot import naocontrols

# Main method starts the Meta Quest 2 and NAO robot links
def main():

    #Starts the websocket server in the background.
    serverThread = threading.Thread(target=vrtrackingserver.ControllerDataServer.startServer())
    serverThread.daemon = True
    serverThread.start()

    #naocontrols.runControls()

if __name__ == "__main__":
    main()