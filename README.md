# Multimodal Feedback in Virtual Reality Based Humanoid Robot Teleoperation
Year 5 Thesis Project Swansea University

IDE Recommendations:

1. Pycharm -> Python
2. VSCode -> C# for Unity

Hardware:

1. Meta Quest 2
2. NAO Robot -> If running with a physical robot

External Software:

1. SideQuest -> https://sidequestvr.com/
2. Meta Horizon -> https://horizon.meta.com/
3. Choregraphe => https://maxtronics.com/en/choregraphe-software/
4. Webots => https://cyberbotics.com/

Set Up Instructions:

1. Install Python 2.7 this can be found following this link: https://www.python.org/downloads/release/python-2718/
2. Install naoqi for python and ensure the framework is within your system path, instructons can be found on aldebarans website linked below: http://doc.aldebaran.com/2-5/dev/python/install_guide.html
3. If using a physcial NAO connect to the computer using an ethernet cable, the port for NAO can be found on the back of his head. If using a virtual NAO, open Choregraphe and connect to a robot on '127.0.0.1' with the port 9559. Additionally, open webots and select the NAO Controller
4. Clone this repository.
5. Connect the Meta Quest 2 to the computer using a thunderbolt 3/4 capable USB-C cable then using SideQuest install the VRTracking.apk file onto the headset.
6. Verify the NAO connection by running the naotest.py file
7. Open Pycharm and run the main file
8. Run the .apk which can be found in the unknown sources section in the Meta Quest Menu
9. In the Unity environment you should be in a room with a screen in front of you and two Meta Quest controllers moving to show hand positioning.
10. Move the headset up slight and follow the calibration instructions displayed in the PyCharm terminal.
11. Once calibrated the robot should begin mimicking your movements and a videofeed from the NAO robot will be displayed on the screen.
