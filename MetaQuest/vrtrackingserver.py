from threading import Lock
import socket

class ControllerDataServer(object):
    controllerData = None
    lock = Lock()

    @staticmethod
    def startServer():
        port = 5005

        socketServer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        socketServer.bind(('0.0.0.0', port))

        print("Server Listening on UDP port "+ str(port) + "...")

        while True:
            data, address = socketServer.recvfrom(1024)

            with ControllerDataServer.lock:
                ControllerDataServer.controllerData = data

            print("Received: ", data)

    @staticmethod
    def getData():
        with ControllerDataServer.lock:
            return ControllerDataServer.controllerData


