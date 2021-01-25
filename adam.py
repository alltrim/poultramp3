import serial
import time

DEVSERIAL = "/dev/tty.usbserial-1410"
#DEVSERIAL = "/dev/ttyS1"

ser = serial.Serial(DEVSERIAL, baudrate=9600, timeout=1)
ser.timeout

while True:
    ser.write(b'$016\x0D')

    resp = ser.read_until(expected=serial.CR)
    print(resp)
    time.sleep(1)
