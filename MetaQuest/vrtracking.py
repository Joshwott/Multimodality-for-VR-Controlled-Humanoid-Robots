from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json

class ControllerDataServer(WebSocket):
    def handleMessage(self):
        try:
            data = json.loads(self.data)
            print("Controller: ", data['controller'])
            print("  Position: ", data['position'])
            print("  Orientation:", data['orientation'])
        except ValueError:
            print("Invalid JSON Received: ", self.data)

    def handleConnected(self):
        print(self.address, "Connected")

    def handleClose(self):
        print(self.address, "Disconnected")

def startServer():
        server = SimpleWebSocketServer('0.0.0.0', 5005, ControllerDataServer)
        print("Server Started")
        server.serveforever()
