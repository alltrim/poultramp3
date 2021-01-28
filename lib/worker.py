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
        self._Trigger = False

        self._session = session
        self._scales = scales
        self._role = role               #role: 1 - gross, 2 - tare, 3 - manual

        self._scales.attachDisconnectCallback(self.onDisconnect)

        if not os.path.exists(self.__DATA_DIR):
            os.mkdir(self.__DATA_DIR)

    def run(self):
        if not self._isRunning:
            if not self._scales.isDiabled():
                self._isRunning = True
                if self._scales.connect():
                    self.loop()

    def setup(self):
        self._KeyboardInitReq = True
        self._WeightingDisplaing = 0
        self._WeightingResult = 0.0
        self._WeightingStarted = False
        self._WeightingComlited = False
        self._currentQty = 0

    def loop(self):
        self.setup()
        while self._isRunning:
            try:
                if self._KeyboardInitReq: 
                    self.KeyboardInit()

                res, status = self._scales.readStatusRegister()
                if res:
                    if status[0] == "B":
                        self.setup()
                        continue

                    elif status[0] == "D":
                        self.DeleteRecord()
                        self._scales.delay(0.5)
                    
                    if status[1:3] == "1A":
                        if self._session.Article == "D":
                            self._session.Article = "C"
                        elif self._session.Article == "C" and self._role == 3:
                            self._session.Article = "E"  
                        else:
                            self._session.Article = "D"
                        self._scales.delay(0.5)

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

                    if bufstate[5] == "1":
                        r, code = self._scales.getF4Code()
                        if r:
                            f4 = int(code)
                            if self._session.LotID:
                                if self._session.Article == "D":
                                    self._session.DeadQty = f4
                                else:
                                    self._currentQty = f4
                    
                    if bufstate[12] == "1":
                        r, wt = self._scales.getWeight()
                        if r:
                            self.OnStabilization(wt)

                now = datetime.datetime.now()

                lot = "----" if self._session.LotID==0 else "{0:d}".format(self._session.LotID)
                tm = now.strftime("%H:%M") if now.microsecond>=500000 else now.strftime("%H %M")
                display = "Lot N: {0:<8}{1:<5}\n".format(lot, tm)

                if self._session.Article == "D":
                    item = "Dead chicken"
                    wt = self._session.DeadWeight
                    qty = self._session.DeadQty
                else:
                    if self._role==2 or self._session.Article == "E":
                        item = "Empty cage"
                        wt = self._session.TareWeight
                        qty = self._session.TareQty
                    else:
                        item = "Chicken in cage"
                        wt = self._session.TotalWeight
                        qty = self._session.TotalQty
                        

                display += "Total: {0:d}/{1:.3f}\n".format(qty, wt)
                display += "{0:<20}\n".format(item)

                if self._WeightingDisplaing > 0:
                    self._WeightingDisplaing -= 1
                    display += "# {0:.3f}".format(self._WeightingResult)
                else:
                    display += "Art Tar      "
                    if self._currentQty == 0:
                        display += "Qty "
                    else:
                        display += "*{0:<3d}".format(self._currentQty)
                    display += "Beg" if self._session.LotID==0 else "End"

                self._scales.display(display)

                self.CheckTrigger()

            except ConnectionResetError:
                break
        
        if self._isRunning:
            self.doRestart()

    def onDisconnect(self):
        raise ConnectionResetError()           

    def doRestart(self):
        if self._isRunning:
            if self._scales.connect():
                self.loop()    

    def KeyboardInit(self):
        res = self._scales.keyboardConfig("0922210006000001")
        if res:
            self._KeyboardInitReq = False
            self._scales.display("Keyboard init: OK")  
        else:
	        self._scales.display("Keyboard init: Fail")
        self._scales.buzz(True)
        return res

    def onTrigger(self):
        self._Trigger = True
        print(self._role, "On trigger")

    def CheckTrigger(self):
        sw = self._Trigger
        self._Trigger = False
        if sw:
            self.StartWeighting()

    def StartWeighting(self):
        if not self._WeightingStarted and not self._WeightingComlited and self._WeightingDisplaing == 0:
            self._WeightingStarted = True
            self.DoWeighting()

    def DoWeighting(self):
        self._WeightingStarted = False
        self._WeightingResult = 0.0
        summa = 0.0
        n = 0
        self._scales.display("#")
        self._scales.triggerDelay()
        while n < 10:
            r, wt = self._scales.getCurrentWeight()
            if r:
                n += 1
                summa += wt
                self._WeightingResult = summa / float(n)
        self._scales.display("{:.3f}".format(self._WeightingResult))
        self._WeightingComlited = True
        self._WeightingDisplaing = 8
        self.AddRecord()

    def OnStabilization(self, wt: float):
        if self._session.LotID == 0:
            return
        if self._session.Article == "D":
            self._session.DeadWeight += wt
        else:
            self._WeightingStarted = False
            self._WeightingComlited = True
            self._WeightingResult = wt
            self._WeightingDisplaing = 8
            self.AddRecord()

    def AddRecord(self):
        self._WeightingComlited = False
        print("Adding", self._WeightingResult)

        lot = self._session.LotID
        art = self._session.Article
        if lot == 0 or art == "D" or self._WeightingResult < 3.0:
            return
        now = datetime.datetime.now()
        filename = self.getFileName(lot)
        qty = 1 if self._currentQty==0 else self._currentQty
        wt = self._WeightingResult
        
        role = self._role
        #if self._role == 3:
        #    if art == "E":
        #        role = 2
        #    else:
        #        role = 1
        #else:
        #    role = self._role

        try:
            with open(filename, "a") as file:
                rec = "{0:d};{1:%Y.%m.%d %H:%M:%S};{2};{3:d};{4:.3f}\r\n".format(role, now, art, qty, wt)
                file.write(rec)
            self._currentQty = 0
            self._session.BeginUpdate()
            if role == 1:
                self._session.TotalWeight += wt
                self._session.TotalQty += qty
            elif role == 3 and art == "C":
                self._session.TotalWeight += wt
                self._session.TotalQty += qty
            else:
                self._session.TareWeight += wt
                self._session.TareQty += qty
            self._session.EndUpdate()

        except Exception as ex:
            print(ex)
            print("Error in file "+filename)
            self.fileOpenError(filename)


    def DeleteRecord(self):
        if self._session.LotID == 0:
            return
        if self._session.Article == "D":
            self._session.BeginUpdate()
            self._session.DeadWeight = 0.0
            self._session.DeadQty = 0
            self._session.EndUpdate()
        elif self._role == 3:
            pass
            #try:
            #    self._deleteLastRecord()
            #except Exception as ex:
            #    print("Record deletion failed:", ex)
            #    self.recordDeletionError()

    def _deleteLastRecord(self):
        lot = self._session.LotID
        art = self._session.Article
        wt = 0.0
        qty = 0

        filename = self.getFileName(lot)
        with open(filename, "r+") as file:
            newrecords = []
            records = file.readlines()
            records.reverse()
            for record in records:
                fields = record.split(sep=";")
                if int(fields[0]) == 3 and fields[2] == art:
                    qty = int(fields[3])
                    wt = float(fields[4])
                    continue
                newrecords.append(record)
            newrecords.reverse()
            file.truncate(0)
            file.writelines(newrecords)

        self._session.BeginUpdate()
        if art == "C":
            self._session.TotalQty -= qty
            self._session.TotalWeight -= wt
        else:
            self._session.TareQty -= qty
            self._session.TareWeight -= wt
        self._session.EndUpdate()

    def recordDeletionError(self):
        self._scales.display("Can't delete")
        self._scales.buzz(True)
        self._scales.delay(5)         
        
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
        
        self._currentQty = 0
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
        #role = 2 if self._role==2 else 1
        role = self._role 
        now = datetime.datetime.now()
        filename = self.getFileName(lot)
        try:
            with open(filename, "a") as file:
                rec = "{0:d};{1:%Y.%m.%d %H:%M:%S};D;{2:d};{3:.3f}\r\n".format(role, now, self._session.DeadQty, self._session.DeadWeight)
                file.write(rec)
            self._session.LotID = 0
            self._currentQty = 0

        except Exception as ex:
            print(ex)
            print("Error in file "+filename)
            self.fileOpenError(filename)
