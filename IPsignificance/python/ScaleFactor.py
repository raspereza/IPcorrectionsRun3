import ROOT
from array import array
import os

class ScaleFactor:

    def __init__(self,**kwargs):
        self.filename = kwargs.get('filename','None')
        if os.path.isfile(self.filename):
            print('Loading file with scale factors for IPSig cut : %s'%(self.filename))
        else:
            print('No file %s is found'%(self.filename))
            print('Quitting')
            exit()
        self.interpolate = kwargs.get('interpolate',False)
        self.sfFile = ROOT.TFile(self.filename,'read')
        self.eff_data = self.sfFile.Get('effData')
        self.eff_mc = self.sfFile.Get('effMC')
        self.nbinsPt = self.eff_data.GetNbinsX()
        self.nbinsEta = self.eff_data.GetNbinsY()
        self.minPt = self.eff_data.GetXaxis().GetBinLowEdge(1)
        self.maxPt = self.eff_data.GetXaxis().GetBinLowEdge(self.nbinsPt+1)
        self.minEta = self.eff_data.GetYaxis().GetBinLowEdge(1)
        self.maxEta = self.eff_data.GetYaxis().GetBinLowEdge(self.nbinsEta+1)
        self.binsEta = []
        self.binsEta.append(self.minEta)
        for ib in range(1,self.nbinsEta+1):
            self.binsEta.append(self.eff_data.GetYaxis().GetBinCenter(ib))
        self.binsEta.append(self.maxEta)
        self.nbinsInterpEta = self.nbinsEta + 1
        self.EtaBinning = ROOT.TH1D('EtaBinsInterp',"",self.nbinsInterpEta,array('d',list(self.binsEta)))
        print('nbinsPt  = %1i'%(self.nbinsPt))
        print('nbinsEta = %1i'%(self.nbinsEta))
        print('minPt    = %2.0f'%(self.minPt))
        print('maxPt    = %2.0f'%(self.maxPt))
        print('minEta   = %4.2f'%(self.minEta))
        print('maxEta   = %4.2f'%(self.maxEta))
        self.hfits = {}
        self.funcs = {}
        self.variations = {'central','up','down'}
        for i in range(1,self.nbinsEta+1):
            istr = '%1i'%(i)
            histname ='hfit_binEta%s'%(istr)
            self.hfits[i] = self.sfFile.Get(histname)
            ff = {}
            for s in self.variations:
                funcname = 'fitFunc_binEta%s_%s'%(istr,s)
                ff[s] = self.sfFile.Get(funcname)
            self.funcs[i] = ff
        
    def getSF(self,pt,eta,**kwargs):
        syst = kwargs.get('syst','central')
        absEta = abs(eta)
        if syst not in self.variations:
            syst = 'central'
        Eta = ROOT.TMath.Min(absEta,self.maxEta-0.001)
        Pt = ROOT.TMath.Max(self.minPt+0.01,ROOT.TMath.Min(pt,self.maxPt-0.01))
        binEta = self.eff_data.GetYaxis().FindBin(Eta)
        bin_id = self.EtaBinning.GetXaxis().FindBin(Eta)
        sf = 1.0

        if self.interpolate:
            if bin_id==1:
                sf = self.funcs[1][syst].Eval(Pt)
                if sf<0: sf = 0.01 # protection against negative values
            elif bin_id==self.nbinsInterpEta:
                sf = self.funcs[self.nbinsEta][syst].Eval(Pt)
                if sf<0: sf = 0.01 # protection against negative values
            else:
                # interpolate SF between eta bins 
                bin1 = bin_id-1
                bin2 = bin_id
                x1 = self.EtaBinning.GetXaxis().GetBinLowEdge(bin_id)
                x2 = self.EtaBinning.GetXaxis().GetBinLowEdge(bin_id+1)
                dx = x2 - x1
                sf1 = self.funcs[bin1][syst].Eval(Pt)
                sf2 = self.funcs[bin2][syst].Eval(Pt)
                if sf1<0: sf1 = 0.01 # protection against negative values
                if sf2<0: sf2 = 0.01 # protection against negative values
                dsf = sf2 - sf1
                dsf_dx = dsf/dx
                sf = sf1 + dsf_dx*(Eta-x1)
        else:
            sf = self.funcs[binEta][syst].Eval(Pt)
        return sf
        
    def getSF_hist(self,pt,eta,**kwargs):
        syst = kwargs.get('syst','central')
        absEta = abs(eta)
        Eta = ROOT.TMath.Min(absEta,self.maxEta-0.001)
        Pt = ROOT.TMath.Max(self.minPt+0.01,ROOT.TMath.Min(pt,self.maxPt-0.01))
        binEta = self.eff_data.GetYaxis().FindBin(Eta)
        bin_id = self.EtaBinning.GetXaxis().FindBin(Eta)
        sf = 1.0
        if bin_id==1:
            bin_pt = self.hfits[1].GetXaxis().FindBin(Pt)
            sf = self.hfits[1].GetBinContent(bin_pt)
            if syst=='up':
                sf += self.hfits[1].GetBinError(bin_pt)
            elif syst=='down':
                sf -= self.hfits[1].GetBinError(bin_pt)
                if sf<0: sf = 0.01 # protection against negative values
        elif bin_id==self.nbinsInterpEta:
            bin_pt = self.hfits[self.nbinsEta].GetXaxis().FindBin(Pt)
            sf = self.hfits[self.nbinsEta].GetBinContent(bin_pt)
            if syst=='up':
                sf += self.hfits[1].GetBinError(bin_pt)
            elif syst=='down':
                sf -= self.hfits[1].GetBinError(bin_pt)
                if sf<0: sf = 0.01 # protection against negative values
        else:
            bin1 = bin_id-1
            bin2 = bin_id
            x1 = self.EtaBinning.GetXaxis().GetBinLowEdge(bin_id)
            x2 = self.EtaBinning.GetXaxis().GetBinLowEdge(bin_id+1)
            dx = x2 - x1
            bin_pt = self.hfits[bin1].GetXaxis().FindBin(Pt)
            sf1 = self.hfits[bin1].GetBinContent(bin_pt)
            sf2 = self.hfits[bin2].GetBinContent(bin_pt)
            if syst=='up':
                sf1 += self.hfits[bin1].GetBinError(bin_pt)
                sf2 += self.hfits[bin2].GetBinError(bin_pt)
            elif syst=='down':
                sf1 -= self.hfits[bin1].GetBinError(bin_pt)
                sf2 -= self.hfits[bin2].GetBinError(bin_pt)
                if sf1<0: sf1 = 0.01 # protection against negative values
                if sf2<0: sf2 = 0.01 # protection against negative values
            dsf = sf2 - sf1
            dsf_dx = dsf/dx
            sf = sf1 + dsf_dx*(Eta-x1)
        return sf
        
    def getEffData(self,pt,eta):
        ptX = pt
        etaX = abs(eta)
        if ptX<self.minPt: ptX = self.minPt+0.01
        if ptX>self.maxPt: ptX = self.maxPt-0.01
        if etaX<self.minEta: etaX = self.minEta+0.01
        if etaX>self.maxEta: etaX = self.maxEta-0.01
        eff = self.eff_data.GetBinContent(self.eff_data.FindBin(ptX,etaX))
        return eff

    def getEffMC(self,pt,eta):
        ptX = pt
        etaX = abs(eta)
        if ptX<self.minPt: ptX = self.minPt+0.01
        if ptX>self.maxPt: ptX = self.maxPt-0.01
        if etaX<self.minEta: etaX = self.minEta+0.01
        if etaX>self.maxEta: etaX = self.maxEta-0.01
        eff = self.eff_mc.GetBinContent(self.eff_mc.FindBin(ptX,etaX))
        return eff

    def getBinnedSF(self,pt,eta):
        ptX = pt
        etaX = abs(eta)
        if ptX<self.minPt: ptX = self.minPt+0.01
        if ptX>self.maxPt: ptX = self.maxPt-0.01
        if etaX<self.minEta: etaX = self.minEta+0.01
        if etaX>self.maxEta: etaX = self.maxEta-0.01
        effData = self.eff_data.GetBinContent(self.eff_data.FindBin(ptX,etaX))
        effMC = self.eff_mc.GetBinContent(self.eff_mc.FindBin(ptX,etaX))
        sf = 1.0
        if effData>0 and effMC>0:
            sf = effData/effMC
        return sf
    

    
