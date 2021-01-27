# coding=cp1251

from threading import Thread
import time
import serial

class ADAM4050(Thread):
    #constructor
    def __init__(self, config):
        Thread.__init__(self)

        self._serial = None
        self.DI = [1 * 8]
        self.DO = [0 * 8]

        self._disabled = True

        self._port = config.get("port", "/dev/ttyS1")
        self._baudrate = int(config.get("baud", "9600"))
        self._bits = int(config.get("bits", "8"))
        self._parity = config.get("parity", "N")
        self._stopbits = int(config.get("stopbits", "1"))
        self._addr = int(config.get("addr", "1"))
        self._grosspin = int(config.get("grosspin", "0"))
        self._tarepin = int(config.get("tarepin", "1"))
        
        disabled = int(config.get("disabled", "1"))
        if disabled == 0:
            self._disabled = False

    def run(self):
        if not self._disabled:
            self.setup()
            self.loop()

    def setup(self):
        if self._disabled:
            return
        
        try:
            if self._serial:
                self._serial.close()
        except Exception:
            pass

        self._serial = serial.Serial(port=self._port, \
            baudrate=self._baudrate, bytesize=self._bits, \
            parity=self._parity, stopbits=self._stopbits, timeout=0.1)
        self._serial.flush()

    def loop(self):
        while True:
            mes = bytes("$016\r", encoding="ascii")
            self._serial.write(mes)
            print(mes)

            resp = self._serial.read_until(serial.CR)
            self.parseDI(resp)
            print(resp)
            time.sleep(0.1) 

    def parseDI(self, resp):
        pass
