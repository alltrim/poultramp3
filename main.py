import signal
import subprocess
from time import sleep


def term_handler(signum, frame):
    global still_working
    still_working = False

still_working = True
signal.signal(signal.SIGTERM, term_handler)

print("\33[32m\33[1mPOULTRAMP3\33[0m: Run")

proc_web = subprocess.Popen(["python", "web/webserver.py"])
proc_app = subprocess.Popen(["python", "lib/app.py"])

try:
    while still_working:
        sleep(1)
except:
    pass
finally:
    print("\33[32m\33[1mPOULTRAMP3\33[0m: Exit")