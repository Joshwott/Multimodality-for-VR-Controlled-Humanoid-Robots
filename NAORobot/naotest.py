from naoqi import ALProxy
import naoconnection


tts = ALProxy("ALTextToSpeech", naoconnection.getRobotIP(),
              naoconnection.getRobotPort())

tts.say("Hello, world!")