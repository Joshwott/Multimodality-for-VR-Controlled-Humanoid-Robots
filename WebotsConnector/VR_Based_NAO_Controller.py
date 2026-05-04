"""VR_Based_NAO_Controller controller."""

from controller import Robot, Camera
import socket, json, struct

PORT = 8080
PYCHARM_IP = "127.0.0.1"
PYCHARM_PORT = 9090
MAX_PACKET_SIZE = 60000

# create the Robot instance.
robot = Robot()
print("[Robot name] " + robot.getName())

# get the time step of the current world.
timestep = int(robot.getBasicTimeStep())

camera = None
for i in range(robot.getNumberOfDevices()):
    device = robot.getDeviceByIndex(i)
    if device.getName() == "CameraTop":
        camera = device
        break

if camera is None:
    print("Camera not found!")
else:
    print("Camera found!")
    camera.enable(timestep)

#Gettin the joints,.
for i in range(robot.getNumberOfDevices()):
    device = robot.getDeviceByIndex(i)
    name = device.getName()
    node_type = device.getNodeType()
    
motors = {}
for i in range(robot.getNumberOfDevices()):
    device = robot.getDeviceByIndex(i)
    if device.getNodeType() == 53:
        motors[device.getName()] = device

# Joint Sockets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", PORT))
sock.setblocking(False)
print("Webots Listening for joint angles on UDP: " + str(PORT))
 
camSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while robot.step(timestep) != -1:
    try:
        latest = None
        while True:
            try:
                data, _ = sock.recvfrom(4096)
                latest = data
            except socket.error:
                break
        if latest:
            joints = json.loads(latest.decode())
            
            for name, angle in joints.items():
                if name in motors:
                    motors[name].setPosition(float(angle))
                    
    except Exception as e:
        print("[Webots] Error: " + str(e))

    try:
        image = camera.getImage()
        width = camera.getWidth()
        height = camera.getHeight()
        
        camera.saveImage("frame.jpg", 70)
        
        with open("frame.jpg", "rb") as f:
            data = f.read()
        
        size = len(data)
        camSock.sendto(struct.pack("<I", size), (PYCHARM_IP, PYCHARM_PORT))
        for i in range(0, size, MAX_PACKET_SIZE):
            camSock.sendto(data[i:i + MAX_PACKET_SIZE], (PYCHARM_IP, PYCHARM_PORT))
    
    except Exception as e:
        print("[Webots] Camera error: " + str(e))