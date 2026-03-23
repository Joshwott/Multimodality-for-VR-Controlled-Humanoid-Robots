from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from threading import Lock
import json

class ControllerDataServer(WebSocket):
    controllerData = None
    lock = Lock()

    def handleMessage(self):
        try:
            data = json.loads(self.data)
            with ControllerDataServer.lock:
                ControllerDataServer.controllerData = data

        except ValueError:
            print("Invalid JSON Received: ", self.data)

    def handleConnected(self):
        print("User connected with address: ", self.address)

    def handleClose(self):
        print("User disconnected with address: ", self.address)

def startServer():
        server = SimpleWebSocketServer('0.0.0.0', 5005, ControllerDataServer)
        print("Server Started...")
        server.serveforever()


