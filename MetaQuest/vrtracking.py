from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
import json

class ControllerDataServer(WebSocket):
    def receiveMessage(self):
        try:
            data = json.loads(self.data)
            print("Controller: ", data['controller'])
            print("  Position: ", data['position'])
            print("  Orientation:", data['orientation'])
        except ValueError:
            print("Invalid JSON Received: ", self.data)

    def connected(self):
        print(self.address, "Connected")

    def disconnected(self):
        print(self.address, "Disconnected")

def startServer():
        server = SimpleWebSocketServer('0.0.0.0', 8000, ControllerDataServer)
        print("Server Started")
        server.serveforever()
