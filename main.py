#Streaming Server for ESP32 Sense

import network
import socket
import time
from camera import Camera

SSID = ""
PASSWORD = ""
CLIENT_IP = "192.168.0.11"  # your PC IP
PORT = 5000

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)
print("Connecting...")
for _ in range(20):
    if wifi.isconnected():
        break
    time.sleep(0.5)
print("Connected:", wifi.ifconfig()[0])

cam = Camera()
cam.init()
cam.set_vflip(True)
cam.set_hmirror(True)
print("Sensor:", cam.get_sensor_name())

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Streaming UDP to", CLIENT_IP, PORT)

while True:
    img = cam.capture()
    if img:
        sock.sendto(bytes(img), (CLIENT_IP, PORT))


