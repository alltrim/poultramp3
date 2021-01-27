# coding=cp1251

from threading import Thread
import time
import serial

class ADAM4050(Thread):
    #constructor
    def __init__(self, config):
        Thread.__init__(self)
        
        self._grosspincallback = None
        self._tarepincallback = None

        self._serial = None
        self.DI = [1 for _ in range(7)]
        self.DO = [0 for _ in range(8)]

        self._disabled = True

        self._port = config.get("port", "/dev/ttyS1")
        self._baudrate = int(config.get("baud", "9600"))
        self._bits = int(config.get("bits", "8"))
        self._parity = config.get("parity", "N")
        self._stopbits = int(config.get("stopbits", "1"))
        self._grosspin = int(config.get("grosspin", "0"))
        self._tarepin = int(config.get("tarepin", "1"))
        
        addr = int(config.get("addr", "1"))
        self._addr = bytes("{0:0=2d}".format(addr), encoding="cp1251")

        disabled = int(config.get("disabled", "1"))
        if disabled == 0:
            self._disabled = False

    def run(self):
        if not self._disabled:
            self.setup()
            self.loop()

    def attachGrossPinCallback(self, callback):
        if callback:
            self._grosspincallback = callback

    def attachTarePinCallback(self, callback):
        if callback:
            self._tarepincallback = callback

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
            req = b'$' + self._addr + b'6' + serial.CR
            self._serial.write(req)
            resp = self._serial.read_until(serial.CR, 8)
            self.parseDI(resp)
            time.sleep(0.1) 

    def parseDI(self, resp):
        #!007F00\r
        sresp = resp.decode(encoding="ascii")
        if len(sresp) < 8:
            return
        if sresp[0] == "!":
            io16 = int(sresp[3:5], base=16)
            for i in range(7):
                bit = io16 & 1
                io16 >>= 1
                if self.DI[i] == 1 and bit == 0:
                    self.onFalling(i)
                self.DI[i] = bit

    def onFalling(self, pin):
        print("Falling", pin)
        if pin == self._grosspin:
            if self._grosspincallback:
                self._grosspincallback()
        elif pin == self._tarepin:
            if self._tarepincallback:
                self._tarepincallback()

