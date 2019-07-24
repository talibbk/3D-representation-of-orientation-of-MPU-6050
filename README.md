**Circuit Connection:**

5V -> VCC
GND -> GND
A4 -> SDA
A5 -> SCL
Pin 2 -> INT

**Prerequisite Python Libraries:**
* PyOpenGL
* Pygame
* pySerial

(make sure to intall libraries compatible with current version of python installed.)

Upload arduino_imu_firmware.ino in arduino IDE.

Run boxctrl_6d0f_imu.py after changing the serial port number.

Press 's' to toggle data recording into CSV file.
Press 'a' to toggle axes display.

Based on work of mattz

