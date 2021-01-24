# coding=cp1251

from threading import Thread
import time
import datetime
import os

class Worker(Thread):
    __DATA_DIR = "./data/"

    #constructor
    def __init__(self, session, scales, role):
        Thread.__init__(self)

        self._isRunning = False

        self._session = session
        self._scales = scales
        self._role = role               #role: 1 - gross, 2 - tare

        if not os.path.exists(self.__DATA_DIR):
            os.mkdir(self.__DATA_DIR)

    def run(self):
        if not self._isRunning:
            if not self._scales.isDiabled():
                self._isRunning = True
                self.loop()

    def loop(self):

        self._KeyboardInitReq = True
        self._WeightingDisplaing = 0

        while self._isRunning:
            
            if self._KeyboardInitReq: 
                self.KeyboardInit()

            res, status = self._scales.readStatusRegister()
            if res:
                if status[0] == "D":
                    self.DeleteRecord()
                
                if status[1:3] == "1A":
                    if self._session.Article == "D":
                        self._session.Article = "C" #if self._role==1 else "E"
                    else:
                        self._session.Article = "D"

            res, bufstate = self._scales.readBufferStateRegister()
            if res:
                if bufstate[3] == "1":
                    r, code = self._scales.getF5Code()
                    if r:
                        f5 = int(code)
                        if self._session.LotID == 0:
                            self.OpenLot(f5)
                        else:
                            self.CloseLot(f5)


            now = datetime.datetime.now()

            lot = "----" if self._session.LotID==0 else "{0:d}".format(self._session.LotID)
            tm = now.strftime("%H:%M") if now.microsecond>=500000 else now.strftime("%H %M")
            display = "Lot N: {0:<8}{1:<5}\n".format(lot, tm)

            if self._session.Article == "D":
                item = "Dead chicken"
                wt = self._session.DeadWeight
                qty = self._session.DeadQty
            else:
                if self._role==1:
                    item = "Chicken in cage"
                    wt = self._session.TotalWeight
                    qty = self._session.TotalQty
                else:
                    item = "Empty cage"
                    wt = self._session.TareWeight
                    qty = self._session.TareQty

            display += "Total: {0:d}/{1:.3f}\n".format(qty, wt)
            display += "{0:<20}\n".format(item)

            if self._WeightingDisplaing > 0:
                pass
            else:
                display += "Art Tar      Qty "
                display += "Beg" if self._session.LotID==0 else "End"

            self._scales.display(display)

            self.CheckTrigger()
                

    def KeyboardInit(self):
        res = self._scales.keyboardConfig("0922210006000001")
        if res:
            self._KeyboardInitReq = False
            self._scales.display("Keyboard init: OK")  
        else:
	        self._scales.display("Keyboard init: Fail")
        self._scales.buzz(True)
        return res

    def DeleteRecord(self):
        pass

    def CheckTrigger(self):
        pass

    def getFileName(self, lot:int):
        now = datetime.datetime.now()
        year = now.year
        if now.day==1 and now.month==1 and lot > 100:
            year -= 1

        filename = self.__DATA_DIR + "{0:0=4d}{1:0=4d}.csv".format(year, lot)
        return filename

    def fileOpenError(self, filename):
        self._scales.display("Can't open "+filename)
        self._scales.buzz(True)
        self._scales.delay(5)

    def OpenLot(self, lot:int):
        if lot == 0:
            return
        filename = self.getFileName(lot)
        if os.path.exists(filename):
            if os.path.getsize(filename) > 0:
                self._scales.display("Lot alredy exists")
                self._scales.buzz(True)
                self._scales.delay(5)
                return
        
        self._session.BeginUpdate()
        self._session.LotID = lot
        self._session.Article = "C"
        self._session.TotalQty = 0
        self._session.TotalWeight = 0.0
        self._session.TareQty = 0
        self._session.TareWeight = 0.0
        self._session.DeadQty = 0
        self._session.DeadWeight = 0.0
        self._session.EndUpdate()
        
    def CloseLot(self, confirm):
        if confirm == 0:
            return
        lot = self._session.LotID
        now = datetime.datetime.now()
        filename = self.getFileName(lot)
        try:
            with open(filename, "w+") as file:
                rec = "{0:d};{1:%Y.%m.%d %H:%M:%S};D;{2:d};{3:.3f}\r\n".format(self._role, now, self._session.DeadQty, self._session.DeadWeight)
                file.write(rec)
                self._session.LotID = 0

        except Exception as ex:
            print(ex)
            print("Error in file "+filename)
            self.fileOpenError(filename)
