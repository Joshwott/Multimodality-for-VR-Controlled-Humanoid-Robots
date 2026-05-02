import socket
import json

HOST = '127.0.0.1'
PORT = 8080

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def sendJointData(name, angles):

    payload = json.dumps(dict(zip(name, angles))).encode()
    sock.sendto(payload, (HOST, PORT))
