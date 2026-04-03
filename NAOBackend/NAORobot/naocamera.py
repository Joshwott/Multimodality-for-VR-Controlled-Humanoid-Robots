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

    def __init__(self, path):
        self.cap = cv2.VideoCapture(path)

    def getFrame(self):
        ret, frame = self.cap.read()

        if not ret:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.cap.read()

        frame = cv2.resize(frame, (320, 240))

        return frame

    def release(self):
        self.cap.release()


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
    scriptPath = os.path.dirname(os.path.realpath(__file__))

    simVideo = os.path.join(scriptPath, "Frieren.mp4")
    #simAudio = os.path.join(scriptPath, "FrierenAudio.wav")

    MAX_PACKET_SIZE = 60000
    address, udpSocket = unityHandshake()

    unityIP = address[0]
    unityPORT = 5006
    videoAddress = (unityIP, unityPORT)

    if REAL_NAO:
        cameraType = NAOLiveFeed()
    else:
        cameraType = SimulatedLiveFeed(simVideo)
        #pygame.mixer.init()
        #pygame.mixer.music.load(simAudio)
        #pygame.mixer.music.play()

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
