#! /usr/bin/env python3
# Author: Alexei Raspereza (August 2025)
# Testing SFs related to the cut on lepton IP significance

from IPcorrectionsRun3.IPsignificance.ScaleFactor import ScaleFactor
import os

if __name__ == "__main__":
    
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-era','--era',dest='era',default='Run3_2022',choices=['Run3_2022','Run3_2023'])
    parser.add_argument('-lepton','--lepton',dest='lepton',default='PromptE',choices=['PromptE','PromptMu','TauE','TauMu'])
    
    args = parser.parse_args()

    label='promptSF'
    if args.lepton=='TauE' or args.lepton=='TauMu':
        label='tauSF'

    cmssw_base = os.getenv('CMSSW_BASE')
    filename = '%s/src/IPcorrectionsRun3/IPsignificance/data/SF_%s_%s.root'%(cmssw_base,args.lepton,args.era)

    ipsigSF = ScaleFactor(filename=filename,label=label)

    eta_points = [0.2, 0.8, 1.4, 2.0]
    pt_points = [25, 30, 35, 40, 50, 60, 80]

    print('')
    print('%s %s'%(args.era,args.lepton))
    for eta in eta_points:
        print('eta = %3.1f'%(eta))
        for pt in pt_points:
            sf = ipsigSF.getSF(pt,eta)
            sf_up = ipsigSF.getSF(pt,eta,syst='up')
            sf_down = ipsigSF.getSF(pt,eta,syst='down')
            print('  pt = %4.1f GeV -> SF(central) = %6.4f  SF(up) = %6.4f  SF(down) = %6.4f'%(pt,sf,sf_up,sf_down))
