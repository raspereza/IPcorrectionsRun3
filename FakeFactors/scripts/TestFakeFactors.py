#! /usr/bin/env python3
# Author: Alexei Raspereza (November 2025)
# Testing fake factors 

from IPcorrectionsRun3.FakeFactors.FakeFactor import FakeFactor
import os
import correctionlib

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('-channel','--channel',dest='channel',default='mt',choices=['mt','et'])
args = parser.parse_args()

pt_array    = [20,  30, 40, 25]
dm_array    = [1, 2, 10, 0]
njets_array = [0, 1, 2, 7]

FF_Types = ['wj','qcd','mc_top','mc_wj']

print('')
print('Testing json-based interface ... ')
print('')
cmssw_base = os.getenv('CMSSW_BASE')
jsonfilename='%s/src/IPcorrectionsRun3/FakeFactors/JSON/Nov18/FF_Run3_%s_ipcut.json'%(cmssw_base,args.channel)
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
