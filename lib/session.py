# coding=cp1251

import pickle

class Session():
    __FILE_NAME = "session.dat"
    
    #singleton
    __instance = None

    @classmethod
    def getInstance(cls):
        if not cls.__instance:
            cls.__instance = Session()
        return cls.__instance

    #constructor
    def __init__(self):
        self._deferflush = False
        self._session = {
            "lotID" : 0,
            "article" : '',
            "totalQty" : 0,
            "totalWeight" : 0.0,
            "tareQty" : 0,
            "tareWeight" : 0.0,
            "deadQty" : 0,
            "deadWeight" : 0.0
        }

    def Flush(self):
        if not self._deferflush:
            with open(self.__FILE_NAME, "wb") as file:
                pickle.dump(self._session, file, protocol=pickle.HIGHEST_PROTOCOL)   

    def Read(self):
        try:
            with open(self.__FILE_NAME, "rb") as file:
                s = pickle.load(file)        
        except:
            s = {}
        
        self._deferflush = False
        
        self._session["lotID"] = s.get("lotID", 0)
        self._session["article"] = s.get("article", '')
        self._session["totalQty"] = s.get("totalQty", 0)
        self._session["totalWeight"] = s.get("totalWeight", 0.0)
        self._session["tareQty"] = s.get("tareQty", 0)
        self._session["tareWeight"] = s.get("tareWeight", 0.0)
        self._session["deadQty"] = s.get("deadQty", 0)
        self._session["deadWeight"] = s.get("deadWeight", 0.0)
          
    def BeginUpdate(self):
        self._deferflush = True

    def EndUpdate(self):
        self._deferflush = False
        self.Flush()

    #lotID
    @property
    def LotID(self):
        return self._session["lotID"]

    @LotID.setter
    def LotID(self, value):
        self._session["lotID"] = value
        self.Flush()

    #article
    @property
    def Article(self):
        return self._session["article"]

    @Article.setter
    def Article(self, value):
        self._session["article"] = value
        self.Flush()

    #totalQty
    @property
    def TotalQty(self):
        return self._session["totalQty"]

    @TotalQty.setter
    def TotalQty(self, value):
        self._session["totalQty"] = value
        self.Flush()
    
    #tareQty
    @property
    def TareQty(self):
        return self._session["tareQty"]

    @TareQty.setter
    def TareQty(self, value):
        self._session["tareQty"] = value
        self.Flush()
    
    #tareWeight
    @property
    def TareWeight(self):
        return self._session["tareWeight"]

    @TareWeight.setter
    def TareWeight(self, value):
        self._session["tareWeight"] = value
        self.Flush()

    #totalWeight
    @property
    def TotalWeight(self):
        return self._session["totalWeight"]

    @TotalWeight.setter
    def TotalWeight(self, value):
        self._session["totalWeight"] = value
        self.Flush()

    #deadQty
    @property
    def DeadQty(self):
        return self._session["deadQty"]

    @DeadQty.setter
    def DeadQty(self, value):
        self._session["deadQty"] = value
        self.Flush()  

    #deadWeight
    @property
    def DeadWeight(self):
        return self._session["deadWeight"]

    @DeadWeight.setter
    def DeadWeight(self, value):
        self._session["deadWeight"] = value
        self.Flush() 