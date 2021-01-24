# coding=cp1251

import configparser
import time
from session import Session
from dialog import Dialog
from worker import Worker


class App():
    def __init__(self):
        self._isRunning = False
        self._config = configparser.ConfigParser()
        self._session = Session.getInstance()

        self._gross = None
        self._tare = None
        self._trigger = None

    def _readSettings(self):
        cfg = self._config.read("settings.ini")
        if len(cfg) == 0:
            raise RuntimeError("Read failed: 'settings.ini'")

    def _createGross(self):
        try:
            cfg = self._config["Gross"]
            scales = Dialog(cfg)
            self._gross = Worker(self._session, scales, 1)
            self._gross.daemon = True
        except Exception as ex:
            print(ex)
            print("Can't create Gross worker")

    def _createTare(self):
        try:
            cfg = self._config["Tare"]
            scales = Dialog(cfg)
            self._tare = Worker(self._session, scales, 2)
            self._tare.daemon = True
        except Exception as ex:
            print(ex)
            print("Can't create Tare worker")
    
    def _createIO(self):
        pass

    def loop(self):
        while self._isRunning:
            time.sleep(0.05)
            #print("in loop")

        print("out loop")

    def run(self):
        self._session.Read()
        
        self._readSettings()
        self._createGross()
        self._createTare()
        self._createIO() 

        if self._gross:
            self._gross.start()

        if self._tare:
            self._tare.start()

        self._isRunning = True
        self.loop()


def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
    
