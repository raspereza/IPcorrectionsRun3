#! /usr/bin/env python3
# Author: Alexei Raspereza (August 2025)
# Testing SFs related to the cut on lepton IP significance

from IPcorrectionsRun3.IPsignificance.ScaleFactor import ScaleFactor
import os
import correctionlib

labelDict = {
    'PromptMu': ['prompt','muon'],
    'PromptE' : ['prompt','electron'],
    'TauMu'   : ['tauDecay','muon'],
    'TauE'    : ['tauDecay','electron'],
}

indexDict = {
    'prompt' : 0,
    'tauDecay' : 1,
}

if __name__ == "__main__":
    
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-lepton','--lepton',dest='lepton',default='PromptE',choices=['PromptE','PromptMu','TauE','TauMu'])
    parser.add_argument('-pt','--pt',dest='pt',type=float,default=40.)
    
    args = parser.parse_args()

    print('')
    
    cmssw_base = os.getenv('CMSSW_BASE')
    filename = '%s/src/IPcorrectionsRun3/IPsignificance/data/SF_%s_Run3_2022-2023.root'%(cmssw_base,args.lepton)
    jsonfilename = '%s/src/IPcorrectionsRun3/IPsignificance/JSON/IP_Significance_Correction_Run3_2022-2023_%s.json'%(cmssw_base,labelDict[args.lepton][1])

    # TF1-based interface
    ipsigSF = ScaleFactor(filename=filename)

    # correctionlib interface
    cset = correctionlib.CorrectionSet.from_file(jsonfilename)
    corr = cset["ipsig_correction"]

    # index of lepton type to be used in the JSON interface
    # 0 - prompt
    # 1 - tauDecay
    leptype = labelDict[args.lepton][0] # prompt or tau
    index = indexDict[leptype]
    
    eta_points = [-1.9, -1.3, -0.6, 0.6, 1.3, 1.9]

    etabins  = ['etaLt1p0','eta1p0to1p6','etaGt1p6']
    typenames = ['prompt','tauDecay']
    sysnames = []
    for typename in typenames:
        for etabin in etabins:
            sysnames.append('%s_%s_stat'%(typename,etabin))

    pt = args.pt
    print('')
    print('---------------------')
    print('%s : pT = %4.1f'%(args.lepton,args.pt))
    print('---------------------')
    print('')
    # Testing custon TF1-based interface
    print('Testing custom interface : ScaleFactor class ->')
    print('-----+--------+--------+--------')
    print(' eta |  down  |   nom  |   up   ')
    print('-----+--------+--------+--------')
    for eta in eta_points:
        sf = ipsigSF.getSF(pt,eta)
        sf_up = ipsigSF.getSF(pt,eta,syst='up')
        sf_down = ipsigSF.getSF(pt,eta,syst='down')
        print('%4.1f | %6.4f | %6.4f | %6.4f'%(eta,sf_down,sf,sf_up))
    print('-----+--------+--------+--------')

    # Testing correctionlib interface
    print('')
    print('Testing correctionlib ->')
    ptx = []
    ptx.append(pt)
    print('-----+----------------------------+--------+--------+-------')
    print(' eta |       systematics          |  down  |   nom  |  up   ')
    print('-----+----------------------------+--------+--------+-------')
    for eta in eta_points:
        etax = []
        etax.append(eta)
        for sysname in sysnames:
            sf_nom = corr.evaluate(ptx, etax, index, 'nom')[0]
            sf_up = corr.evaluate(ptx, etax, index, sysname+'_up')[0]
            sf_down = corr.evaluate(ptx, etax, index, sysname+'_down')[0]
            print('%4.1f | %26s | %6.4f | %6.4f | %6.4f'%(eta,sysname,sf_down,sf_nom,sf_up))
        print('-----+----------------------------+--------+--------+-------')

