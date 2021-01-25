import serial
import time

#DEVSERIAL = "/dev/tty.usbserial-1410"
DEVSERIAL = "/dev/ttyS1"

ser = serial.Serial(DEVSERIAL, baudrate=9600, timeout=1)
ser.flush()

while True:
    mes = bytes("$016\r", encoding="ascii")
    ser.write(mes)
    print(mes)

    resp = ser.read_until(serial.CR)
    print(resp)
    time.sleep(1)  
