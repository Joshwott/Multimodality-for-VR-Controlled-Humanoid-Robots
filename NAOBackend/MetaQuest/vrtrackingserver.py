from threading import Lock
import socket

#Class containing the UDP Server that the data sends.
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
                try:
                    ControllerDataServer.controllerData = data.decode('utf-8')
                except Exception as e:
                    print("Error decoding data:", e)
                    ControllerDataServer.controllerData = None

            #print(ControllerDataServer.controllerData)

    @staticmethod
    def getData():
        with ControllerDataServer.lock:
            return ControllerDataServer.controllerData