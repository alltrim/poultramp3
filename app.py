import configparser


class App():
    def __init__(self):
        self._running = False
        self._config = configparser.ConfigParser()

        self._gross = None
        self._tare = None
        self._trigger = None

    def _readSettings(self):
        cfg = self._config.read("settings.ini")
        if len(cfg) == 0:
            raise RuntimeError("Read failed: 'settings.ini'")

    def loop(self):
        while self._running:
            print("in loop")
            self._running = False

        print("out loop")

    def run(self):
        self._readSettings()   
        
        self._running = True;
        self.loop()


def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()
    
