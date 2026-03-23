from naoqi import ALProxy
import naoconnection


tts = ALProxy("ALTextToSpeech", naoconnection.getRobotIP(),
              naoconnection.getRobotPort())

tts.say("Hello, world!")

motion = ALProxy("ALMotion", naoconnection.getRobotIP(),
              naoconnection.getRobotPort())

motion.wakeUp()
motion.moveTo(0.5, 0, 0)