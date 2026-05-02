from naoqi import ALProxy
import cv2
import numpy as np
import naoconnection
import pygame, struct, os, socket

REAL_NAO = False

class NAOLiveFeed:

    def __init__(self):
        self.videoFeed = ALProxy("ALVideoDevice", naoconnection.getRobotIP(),
                            naoconnection.getRobotPort())

        camera = 0
        resolution = 2
        colour = 11
        fps = 30

        self.camName = "naoCam"
        self.videoClient = self.videoFeed.subscribeCamera(self.camName, camera, resolution,
                                                colour, fps)

    def getFrame(self):
        image = self.videoFeed.getImageRemote(self.videoClient)

        if image is None:
            return None

        width, height = image[0], image[1]
        array = np.frombuffer(image[6], dtype=np.uint8)
        return array.reshape(height, width, 3)

    def release(self):
        self.videoFeed.unsubscribeCamera(self.videoClient)

class SimulatedLiveFeed:

    def __init__(self, host="127.0.0.1", port=9090):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((host, port))
        self.expectedSize = 0
        self.buffer = b''
        print("Listening for Webots camera on UDP " + str(port))

    def getFrame(self):
        while True:
            data, _ = self.sock.recvfrom(65535)

            if len(data) == 4:
                self.expectedSize = struct.unpack("<I", data)[0]
                self.buffer = b''
                continue

            self.buffer += data

            if len(self.buffer) >= self.expectedSize:
                imageArray = np.frombuffer(self.buffer[:self.expectedSize], dtype=np.uint8)
                return cv2.imdecode(imageArray, cv2.IMREAD_COLOR)

    def release(self):
        self.sock.close()

def unityHandshake():
    print("Waiting for READY handshake...")

    udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udpSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcastPort = 5007
    udpSocket.bind(("", broadcastPort))

    while True:
        data, address = udpSocket.recvfrom(1024)
        if data.decode() == "READY":
            print("Unity READY Received")
            return address, udpSocket


def startCameraClient():

    MAX_PACKET_SIZE = 60000
    address, udpSocket = unityHandshake()

    unityIP = address[0]
    unityPORT = 5006
    videoAddress = (unityIP, unityPORT)

    if REAL_NAO:
        cameraType = NAOLiveFeed()
    else:
        cameraType = SimulatedLiveFeed()

    try:
        fps = 30
        delay = int(1000 / fps)

        while True:
            frame = cameraType.getFrame()

            if frame is None:
                continue

            if REAL_NAO:
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            cv2.imshow("Live Camera Feed", frame)

            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            data = buffer.tobytes()
            size = len(data)

            udpSocket.sendto(struct.pack("<I", size), videoAddress)

            for i in range(0, size, MAX_PACKET_SIZE):
                udpSocket.sendto(data[i:i + MAX_PACKET_SIZE], videoAddress)

            if cv2.waitKey(delay) & 0xFF == ord('q'):
                break

    finally:
        cameraType.release()
        cv2.destroyAllWindows()