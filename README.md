# XIAO ESP32S3 Sense — MicroPython WiFi Camera Streaming Setup

Live wireless camera streaming from the Seeed Studio XIAO ESP32S3 Sense using MicroPython, over UDP to a Python/OpenCV client on your PC.

> **⚠️ Important:** It appears current production XIAO ESP32S3 Sense boards ship with an **OV3660** camera sensor, not OV2640. The official Seeed MicroPython wiki and kaki5 firmware are broken for these boards. This guide uses the correct firmware.

<img width="327" height="243" alt="image" src="https://github.com/user-attachments/assets/10e687a6-08ea-40fe-9457-5bec652568bb" />

---

## Hardware

- Seeed Studio XIAO ESP32S3 Sense (with OV3660 camera)
- USB-C cable (data, not charge-only)
- Linux/Mac/Windows PC
- WiFi network

---

## Step 1 — Download the Correct Firmware

Download the XIAO ESP32S3 firmware from cnadler86's MicroPython camera API:

**[mpy_cam-v1.27.0-XIAO_ESP32S3.zip](https://github.com/cnadler86/micropython-camera-API/releases/download/v0.6.2/mpy_cam-v1.27.0-XIAO_ESP32S3.zip)**

Extract the zip and note the path to `firmware.bin`.

> This firmware has OV3660 support.

---

## Step 2 — Flash the Firmware (your PC)

Install esptool:
```bash
pip install esptool
```

**Enter bootloader mode:**
1. Unplug USB
2. Hold the **B** (Boot) button — it's a tiny SMD button on the top edge of the board, opposite the USB-C port. Use a toothpick or dupont pin 
3. Plug USB back in while holding B
4. Release B after 2 seconds

**Verify bootloader mode (Linux/Mac):**
```bash
dmesg | tail -5
```
Look for `idProduct=4001` and `Espressif Device` — that confirms bootloader mode. Note the port (e.g. `/dev/ttyACM0`).

**Erase and flash:**
```bash
# Erase first
esptool --port /dev/ttyACM0 --baud 115200 --chip esp32s3 erase-flash

# Flash (hold B button again before running this)
esptool --port /dev/ttyACM0 --baud 115200 --chip esp32s3 --before no-reset \
  write-flash --flash-mode dio --flash-size detect --flash-freq 80m \
  0x0 /path/to/firmware.bin
```

On **Windows** replace `/dev/ttyACM0` with `COM3` (or whichever port appears in Device Manager).

**Successful flash output:**
```
Connected to ESP32-S3
Auto-detected flash size: 8MB
Wrote 1948208 bytes at 0x00000000
Hash of data verified.
```

---

## Step 3 — Verify Camera (Thonny)

Install [Thonny IDE](https://thonny.org/), connect to the board (Tools → Options → MicroPython ESP32), and run in the shell:

```python
from machine import SoftI2C, Pin
import time

i2c = SoftI2C(scl=Pin(39), sda=Pin(40), freq=100000)
time.sleep_ms(100)
print([hex(d) for d in i2c.scan()])
```

Expected output: `['0x3c']` — that's your OV3660.

Then test the camera:
```python
from camera import Camera
cam = Camera()
cam.init()
print("Sensor:", cam.get_sensor_name())  # should print OV3660
img = cam.capture()
print("Captured:", len(bytes(img)), "bytes")  # should print 38400
```

---

## Step 4 — Board Code (main.py)

Upload  `main.py` on the board via Thonny. It will auto-run on every boot.

## Step 5 — PC Client

Install dependencies:
```bash
pip install numpy opencv-python
```

```bash
python stream_client.py
```

The UI is .. not so great...here are some shortcuts..

**Controls:**
| Key | Action |
|-----|--------|
| `S` | Save timestamped JPEG snapshot |
| `R` | Start / stop AVI video recording |
| `ESC` | Quit |

---

## Troubleshooting

**`camera.init()` returns False**
You have an OV3660 board but wrong firmware. Flash `mpy_cam-v1.27.0-XIAO_ESP32S3.zip` as described above.

**`Failed to connect to ESP32-S3: No serial data received`**
Board is not in bootloader mode. Close Thonny, retry the B button sequence, then run esptool immediately.

**Port keeps changing (`ttyACM0` → `ttyACM3` etc)**
Another process (Thonny) is holding the port and resetting the board. Close Thonny completely before flashing.

**Horizontal lines in stream**
Use UDP (this guide). TCP fragmentation causes frame boundary drift that produces this artifact.

**`I2C devices found: []`**
Camera ribbon cable not fully seated. Unplug USB, pop the expansion board off and back on firmly, replug.

---

## How It Works

The OV3660 captures raw RGB565 frames (160×120, 2 bytes/pixel = 38400 bytes). These are sent as single UDP datagrams to the PC. The PC client decodes the RGB565 pixel format and upscales for display using OpenCV.

UDP is used instead of TCP because at this frame size each frame fits in a single datagram, avoiding the TCP stream reassembly issues that cause horizontal line artifacts.

---

## Known Limitations

- Native resolution locked at 160×120 (OV3660 + firmware limitation)
- `reconfigure()` and constructor-time `pixel_format=PixelFormat.JPEG` cause init failures on OV3660
- No JPEG output from the board — RGB565 decoded on PC side

---

## Credits

- **cnadler86** — [micropython-camera-API](https://github.com/cnadler86/micropython-camera-API) — the only MicroPython firmware with OV3660 support
- **shariltumin** — various firmwares and pointers / help
- Seeed Studio — [XIAO ESP32S3 hardware](https://wiki.seeedstudio.com/xiao_esp32s3_getting_started/)
- Claude (Anthropic) — spent an evening(s) debugging OV3660 incompatibility, TCP frame artifacts, and RGB565 byte order before arriving at this guide
- https://github.com/Seeed-Studio/wiki-documents/issues/4792





