#! /usr/bin/env python3
# Author: Alexei Raspereza (November 2025)
# Testing fake factors 

from IPcorrectionsRun3.FakeFactors.FakeFactor import FakeFactor
import os
import correctionlib

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('-channel','--channel',dest='channel',default='mt')
parser.add_argument('-ipcut','--ipcut',dest='ipcut',default='noipcut')
args = parser.parse_args()

cmssw_base = os.getenv('CMSSW_BASE')

filename = 'FF_Run3_%s_%s'%(args.channel,args.ipcut)
    
dm_dict = {
    0: 'pi',
    1: 'rho',
    2: 'a1_1pr',
    10: 'a1_3pr',
}

pt_array    = [26.96]
dm_array    = [0]
njets_array = [4.0]

FF_Types = ['wj','qcd','mc_top']

print('')
print('Testing non-vectorised TF1 based interface...')
rootfilename = '%s/src/IPcorrectionsRun3/FakeFactors/data/Nov18/%s.root'%(cmssw_base,filename)
ff_evaluator = FakeFactor(filename=rootfilename)
print('')
for i in range(len(pt_array)):
    njets_label = 'njets2'
    if njets_array[i]==0:
        njets_label = 'njets0'
    if njets_array[i]==1:
        njets_label = 'njets1'
        
    print('pt=%4.1f, dm=%1i, njets=%1i'%(pt_array[i],dm_array[i],njets_array[i]))
    for FF in FF_Types:
        ff = ff_evaluator.getFF(pt_array[i],
                                eta='all',
                                dm=dm_dict[dm_array[i]],
                                njets=njets_label,
                                typ=FF,
                                sys='nom')
        print('  FF(%s) = %6.4f'%(FF,ff))

print('')
print('Testing json-based interface ... ')
print('')
jsonfilename='%s/src/IPcorrectionsRun3/FakeFactors/JSON/Nov18/%s.json'%(cmssw_base,filename)
cset = correctionlib.CorrectionSet.from_file(jsonfilename)
corr = cset['Fake_factors']

fakeF = {}
fakeF_up = {}
fakeF_down = {}
for FF in FF_Types:
    fakeF[FF] = corr.evaluate(pt_array,njets_array,dm_array,FF,'nom')
    fakeF_up[FF] = corr.evaluate(pt_array,njets_array,dm_array,FF,'up')
    fakeF_down[FF] = corr.evaluate(pt_array,njets_array,dm_array,FF,'down')
    
for i in range(len(pt_array)):
    print('pt=%4.1f, dm=%1i njets=%1i'%(pt_array[i],
                                        dm_array[i],
                                        njets_array[i]))
    for FF in FF_Types:
        print('  FF(%s) = %6.4f(nom)  %6.4f(up)  %6.4f(down)'%(FF,
                                                               fakeF[FF][i],
                                                               fakeF_up[FF][i],
                                                               fakeF_down[FF][i]
                                                               ))
