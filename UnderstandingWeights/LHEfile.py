import ROOT as rt

class LHEfile():
    
    def __init__(self, fileINname):
        self.eventList = []
        self.eventWeight = []
        self.fileINname = fileINname
        self.MaxEv = -99

    def setMax(self, maxVal):
        self.Max = maxVal
        
    def readEvents(self):
        fileIN = open(self.fileINname)
        newEVENT = False
        oneEvent = []
        for line in fileIN:
            if newEVENT: oneEvent.append(line)
            if line.find("<mgrwt>") != -1:
                # the event block ends
                newEVENT = False
            if line.find("</event>") != -1:
                newEVENT = False
                self.eventList.append(oneEvent)
                oneEvent = []
                if len(self.eventList) >= self.Max and self.Max>0: break
            if line.find("<event>") != -1:
                # the event block starts
                newEVENT = True
                oneEvent.append(line)
        fileIN.close()
        return self.eventList

    def readWeights(self): 
        fileIN = open(self.fileINname)
        newWEIGHT = False
        oneWeight = []
        for line in fileIN:
            if newWEIGHT: oneWeight.append(line) 
            if line.find("</event>") != -1:
                newWEIGHT = False
            if line.find("</rwgt>") != -1:
                newWEIGHT = False
                self.eventWeight.append(oneWeight)
                oneWeight = []
                #if len(self.eventList) >= self.Max and self.Max>0: break
            if line.find("<rwgt>") != -1:
                newWEIGHT = True
                oneWeight.append(line)
        fileIN.close()
        return self.eventWeight 
