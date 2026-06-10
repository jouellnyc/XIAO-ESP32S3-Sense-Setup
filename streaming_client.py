
import socket
import numpy as np
import cv2

PORT = 5000
W, H = 160, 120

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))
sock.settimeout(5)

print("Listening on UDP port", PORT)

while True:
    data, addr = sock.recvfrom(65535)
    if len(data) != W * H * 2:
        print("bad frame:", len(data))
        continue

    arr = np.frombuffer(data, dtype=np.uint16).reshape(H, W)
    arr = arr.byteswap()
    r = ((arr >> 11) & 0x1F) << 3
    g = ((arr >> 5) & 0x3F) << 2
    b = (arr & 0x1F) << 3
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    bgr = cv2.resize(bgr, (640, 480), interpolation=cv2.INTER_LINEAR)
    cv2.imshow("XIAO Camera", bgr)

    if cv2.waitKey(1) == 27:
        break

sock.close()
cv2.destroyAllWindows()


