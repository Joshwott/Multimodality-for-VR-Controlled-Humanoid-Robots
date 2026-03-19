from naoqi import ALProxy
import cv2
import numpy as np
import naoconnection

videoFeed = ALProxy("ALVideoDevice", naoconnection.getRobotIP(),
                    naoconnection.getRobotPort())

# Setting Parameters for the NAO camera.
camera = 0
resolution = 2
colour = 11
fps = 30

camName = "naoCam"
videoClient = videoFeed.subscribeCamera(camName, camera, resolution,
                                        colour, fps)

try:
    while True:
        image = videoFeed.getImageRemote(videoClient)
        if image is None:
            continue

        imageWidth = image[0]
        imageHeight = image[1]
        array = np.frombuffer(image[6], dtype=np.uint8)
        array = array.reshape(imageHeight, imageWidth, 3)

        cv2.imshow("NAO Live Feed", array)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    videoFeed.unsubscribe(camName)
    cv2.destroyAllWindows()




