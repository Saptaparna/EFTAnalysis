import sys
import ROOT as rt
import math
from LHEevent import *
from LHEfile import *
import plotTools

if __name__ == '__main__':

    #Bprime histograms
    MW_jj = rt.TH1D("MW_jj", "MW_jj", 500, 0., 500)
    MW_jj.Sumw2()
    MInvariantMass_mumu = rt.TH1F("MInvariantMass_mumu", "MInvariantMass_mumu", 500, 0., 500);
    MInvariantMass_mumu.Sumw2()    
    MInvariantMass_qq = rt.TH1F("MInvariantMass_qq", "MInvariantMass_qq", 500, 0., 1000.0);
    MInvariantMass_qq.Sumw2()
    EW_jj = rt.TH1D("EW_jj", "EW_jj", 500, 0., 1000)
    EW_jj.Sumw2()
    EW_qq = rt.TH1D("EW_qq", "EW_qq", 500, 0., 1000)
    EW_qq.Sumw2()
    pTW_jj = rt.TH1D("pTW_jj", "pTW_jj", 500, 0., 500)
    pTW_jj.Sumw2()
    W1_lv = rt.TLorentzVector()
    W2_lv = rt.TLorentzVector()
    W3_lv = rt.TLorentzVector()
    massW_1 = rt.TH1F("massW_1", "massW_1", 500, 0., 500.0)
    massW_1.Sumw2()
    massW_2 = rt.TH1F("massW_2", "massW_2", 500, 0., 500.0)  
    massW_2.Sumw2()    
    massW_3 = rt.TH1F("massW_3", "massW_3", 500, 0., 500.0)  
    massW_3.Sumw2()
    M_www = rt.TH1D("M_www", "M_www", 400, 0.0, 4000.0)
    M_www.Sumw2()

    # find events in file
    myLHEfile = LHEfile(sys.argv[1])
    myLHEfile.setMax(100000)
    #myLHEfile.setMax(2)
    eventsReadIn = myLHEfile.readEvents()
    for oneEvent in eventsReadIn:
        myLHEevent = LHEevent()
        myLHEevent.fillEvent(oneEvent)
        n_mu = 0
        n_q = 0
        n_el = 0
        n_nuel = 0
        mass = []
        for i in range(0,len(myLHEevent.Particles)):
            p = myLHEevent.Particles[i]
            if abs(p['ID'])  == 24: MW_jj.Fill(p['M'])
            if abs(p['ID'])  == 24: EW_jj.Fill(p['E'])
            if (abs(p['ID'])  == 24 and rt.TMath.Sqrt(p['Px']*p['Px'] + p['Py']*p['Py']) > 50.0): pTW_jj.Fill(rt.TMath.Sqrt(p['Px']*p['Px'] + p['Py']*p['Py']))
            if abs(p['ID']) == 24: 
              mass.append(p['M'])
              mass.sort()
              if(len(mass)==1): massW_1.Fill(mass[0])
              if(len(mass)==2): massW_2.Fill(mass[1])
              if(len(mass)==3): massW_3.Fill(mass[2])
              if(len(mass)==1): W1_lv = rt.TLorentzVector(p['Px'], p['Py'], p['Pz'], p['E'])
              if(len(mass)==2): W2_lv = rt.TLorentzVector(p['Px'], p['Py'], p['Pz'], p['E'])
              if(len(mass)==3): W3_lv = rt.TLorentzVector(p['Px'], p['Py'], p['Pz'], p['E'])
              if(len(mass)==3): M_www.Fill((W1_lv+W2_lv+W3_lv).M());
        del oneEvent, myLHEevent
        
    # write the histograms
    histoFILE = rt.TFile(sys.argv[2],"RECREATE")
    MW_jj.Write()
    EW_jj.Write()
    pTW_jj.Write()
    massW_1.Write()
    massW_2.Write()
    massW_3.Write()
    M_www.Write() 
    histoFILE.Close()
