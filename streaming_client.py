
import socket
import numpy as np
import cv2
import time

HOST = "192.168.0.38"
PORT = 5000
W, H = 160, 120
DISPLAY_W, DISPLAY_H = 640, 480

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", PORT))
sock.settimeout(5)
print("Listening on UDP port", PORT)

recording = False
writer = None

while True:
    try:
        data, addr = sock.recvfrom(65535)
    except socket.timeout:
        print("Waiting...")
        continue

    if len(data) != W * H * 2:
        continue

    arr = np.frombuffer(data, dtype=np.uint16).reshape(H, W)
    arr = arr.byteswap()
    r = ((arr >> 11) & 0x1F) << 3
    g = ((arr >> 5)  & 0x3F) << 2
    b = (arr         & 0x1F) << 3
    rgb = np.stack([r, g, b], axis=-1).astype(np.uint8)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    bgr = cv2.resize(bgr, (DISPLAY_W, DISPLAY_H), interpolation=cv2.INTER_LINEAR)

    # write frame if recording
    if recording and writer:
        writer.write(bgr)

    cv2.imshow("XIAO Camera", bgr)

    key = cv2.waitKey(1) & 0xFF

    if key == 27:  # ESC — quit
        break

    elif key == ord('s'):  # s — save snapshot
        fname = f"snapshot_{int(time.time())}.jpg"
        cv2.imwrite(fname, bgr)
        print("Saved:", fname)

    elif key == ord('r'):  # r — toggle recording
        if not recording:
            fname = f"video_{int(time.time())}.avi"
            writer = cv2.VideoWriter(fname, cv2.VideoWriter_fourcc(*'XVID'), 15, (DISPLAY_W, DISPLAY_H))
            recording = True
            print("Recording:", fname)
        else:
            writer.release()
            writer = None
            recording = False
            print("Recording stopped")

if writer:
    writer.release()
sock.close()
cv2.destroyAllWindows()


