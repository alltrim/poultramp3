# coding=cp1251

import socket
import re
import time

class Dialog():
    #constructor
    def __init__(self, config):
        self._disabled = True

        host = config.get("host", "127.0.0.1")
        port = int(config.get("port", "1001"))
        addr = int(config.get("addr", "1"))
        disabled = int(config.get("disabled", "1"))

        if not disabled == 1:
            self._disabled = False
            self._addr = bytes("{0:0=2d}".format(addr), encoding="cp1251")

            self._sock = socket.socket()
            self._sock.settimeout(0.1)
            self._sock.connect((host, port))

    def read(self, size=1):
        try:
            res = self._sock.recv(size)
        except Exception as ex:
            res = b""
        return res

    def write(self, data):
        try:
            res = self._sock.send(data)
        except Exception as ex:
            res = 0
        return res
    
    def isDiabled(self):
        return self._disabled

    def delay(self, sec):
        time.sleep(sec)

    def readUntil(self, terminator):
        resp = b""
        while True:
            b = self.read(1)
            if len(b) == 0 or b == terminator:
                return resp.decode(encoding="cp1251")
            resp += b

    def readStatusRegister(self):
        result = False
        data = ""
        req = b"\x02" + self._addr + b"\x0D{\x80}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        #print(resp)
        if re.match(r"^.{5}$", resp):
            result = True
            data = resp
        return result, data

    def readBufferStateRegister(self):
        result = False
        data = ""
        req = b"\x02" + self._addr + b"\x0D{\x81}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        #print(resp)
        if re.match(r"^[01]{16}$", resp):
            result = True
            data = resp
        return result, data
    
    def getWeight(self):
        result = False
        data = 0.0
        req = b"\x02" + self._addr + b"\x0D{\x8C}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        #print(resp)
        r = re.match(r"^[NS]{0,1}([ +-][ 0-9.]{7}) [ k][g]$", resp)
        if r:
            result = True
            w = r.group(1).replace(r" ", r"")
            data = float(w)   
        return result, data

    def getCurrentWeight(self):
        result = False
        data = 0.0
        req = b"\x02" + self._addr + b"\x0D{\x87}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        #print(resp)
        r = re.match(r"^[NS]{0,1}([ +-][ 0-9.]{7}) [ k][g]$", resp)
        if r:
            result = True
            w = r.group(1).replace(r" ", r"")
            data = float(w)   
        return result, data

    def getTare(self):
        result = False
        data = 0.0
        req = b"\x02" + self._addr + b"\x0D{\x8D}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        r = re.match(r"^([ +-][ 0-9.]{7}) [ k][g]$", resp)
        if r:
            result = True
            w = r.group(1).replace(r" ", r"")
            data = float(w)   
        return result, data

    def getKeyboardBuffer(self):
        req = b"\x02" + self._addr + b"\x0D{\x82}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        result = True
        data = resp   
        return result, data

    def getF1Code(self):
        req = b"\x02" + self._addr + b"\x0D{\x84}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        result = True
        data = resp   
        return result, data

    def getF2Code(self):
        req = b"\x02" + self._addr + b"\x0D{\x86}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        result = True
        data = resp   
        return result, data

    def getF3Code(self):
        req = b"\x02" + self._addr + b"\x0D{\x8A}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        result = True
        data = resp   
        return result, data

    def getF4Code(self):
        req = b"\x02" + self._addr + b"\x0D{\x85}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        result = True
        data = resp   
        return result, data

    def getF5Code(self):
        req = b"\x02" + self._addr + b"\x0D{\x83}"
        time.sleep(0.05)
        self.write(req)
        resp = self.readUntil(b"\0")
        result = True
        data = resp   
        return result, data

    def display(self, text):
        result = False 
        data = ""
        lines = str(text).splitlines(False)
        for ln in lines:
            line = ln + "                    "
            data += line[0:20]
        if len(data) < 80:
            data += "                                                                                "
        data = data[0:80]
        time.sleep(0.05)
        self.write(b"\x02")
        self.write(self._addr)
        self.write(b"\x0D{\xF0\x3F")
        self.write(bytes(data, encoding="cp1251"))
        self.write(b"}")
        resp = self.readUntil(b"}")
        if re.match(r"^OK$", resp):
            result = True
        return result

    def printLabel(self, label):
        result = False
        data = label
        time.sleep(0.2)
        self.write(b"\x02")
        self.write(self._addr)
        self.write(b"\x0D{\xE0")
        self.write(bytes(data, encoding="cp1251"))
        self.write(b"\x00}")
        time.sleep(1.2)
        resp = self.readUntil(b"}")
        if re.match(r"^OK$", resp):
            result = True
        return result

    def buzz(self, blink=False):
        result = False
        data = b"B" if blink else b"b"
        time.sleep(0.2)
        self.write(b"\x02")
        self.write(self._addr)
        self.write(b"\x0D{\xF9")
        self.write(data)
        self.write(b"}")
        resp = self.readUntil(b"}")
        if re.match(r"^OK$", resp):
            result = True
        return result

    # | F1 | F2 | F3 | F4 | F5 | PRINT | F | M+ | MR | CE | ? | ? | ? | ? | PROGRAM | OFF |
    def keyboardConfig(self, config="0900010006000001"):
        result = False
        data = bytes(config, encoding="cp1251")
        time.sleep(0.2)
        self.write(b"\x02")
        self.write(self._addr)
        self.write(b"\x0D{\xF6")
        self.write(data)
        self.write(b"}")
        resp = self.readUntil(b"}")
        if re.match(r"^OK$", resp):
            print("se12: Keyboard config '%s'" % config)
            result = True
        return result

    def keyPress(self, keycode="FF"):
        result = False
        data = bytes(keycode, encoding="cp1251")
        time.sleep(0.2)
        self.write(b"\x02")
        self.write(self._addr)
        self.write(b"\x0D{\xF9C")
        self.write(data)
        self.write(b"}")
        resp = self.readUntil(b"}")
        if re.match(r"^OK$", resp):
            print("se12: Key press '%s'" % keycode)
            result = True
        return result
     
