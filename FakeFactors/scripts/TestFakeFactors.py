#! /usr/bin/env python3
# Author: Alexei Raspereza (November 2025)
# Testing fake factors 

from IPcorrectionsRun3.FakeFactors.FakeFactor import FakeFactor
import os
import correctionlib

cmssw_base = os.getenv('CMSSW_BASE')
filename = '%s/src/IPcorrectionsRun3/FakeFactors/data/FF_Run3_mt_v2.root'%(cmssw_base)

dm_dict = {
    0: 'pi',
    1: 'rho',
    2: 'a1_1pr',
    10: 'a1_3pr',
}

pt_array    = [20,  30, 40, 25]
eta_array   = [0.2, 1.7, -0.2, 2.2]
dm_array    = [1, 2, 10, 0]
njets_array = [0, 1, 2, 7]

FF_Types = ['wj','qcd','mc_top','mc_wj']

print('')
print('Testing non-vectorised TF1 based interface...')
ff_evaluator = FakeFactor(filename=filename)
print('')
for i in range(len(pt_array)):
    absEta = abs(eta_array[i])
    eta_label = 'barrel'
    if absEta>1.48:
        eta_label = 'endcap'
    njets_label = 'njets2'
    if njets_array[i]==0:
        njets_label = 'njets0'
    if njets_array[i]==1:
        njets_label = 'njets1'
        
    print('pt=%4.1f, eta=%3.1f, dm=%1i, njets=%1i'%(pt_array[i],eta_array[i],dm_array[i],njets_array[i]))
    for FF in FF_Types:
        ff = ff_evaluator.getFF(pt_array[i],
                                eta=eta_label,
                                dm=dm_dict[dm_array[i]],
                                njets=njets_label,
                                typ=FF,
                                sys='nom')
        print('  FF(%s) = %6.4f'%(FF,ff))

print('')
print('Testing json-based interface ... ')
print('')
jsonfilename='%s/src/IPcorrectionsRun3/FakeFactors/JSON/FF_Run3_mt_v2.json'%(cmssw_base)
cset = correctionlib.CorrectionSet.from_file(jsonfilename)
corr = cset['Fake_factors']

fakeF = {}
fakeF_up = {}
fakeF_down = {}
for FF in FF_Types:
    fakeF[FF] = corr.evaluate(pt_array,eta_array,njets_array,dm_array,FF,'nom')
    fakeF_up[FF] = corr.evaluate(pt_array,eta_array,njets_array,dm_array,FF,'up')
    fakeF_down[FF] = corr.evaluate(pt_array,eta_array,njets_array,dm_array,FF,'down')
    
for i in range(len(pt_array)):
    print('pt=%4.1f, eta=%3.1f dm=%1i njets=%1i'%(pt_array[i],
                                                  eta_array[i],
                                                  dm_array[i],
                                                  njets_array[i]))
    for FF in FF_Types:
        print('  FF(%s) = %6.4f(nom)  %6.4f(up)  %6.4f(down)'%(FF,
                                                               fakeF[FF][i],
                                                               fakeF_up[FF][i],
                                                               fakeF_down[FF][i]
                                                               ))
