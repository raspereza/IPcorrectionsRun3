#! /usr/bin/env python3
# Author: Alexei Raspereza (November 2025)
# Testing corrections to factors 

from IPcorrectionsRun3.FakeFactors.FFclosure import FFclosure
import os
import correctionlib

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('-channel','--channel',dest='channel',default='mt',choices=['mt','et'])
args = parser.parse_args()

bdt_score  = [0.4, 0.5, 0.6, 0.7]
# BDT class : 0-ditau, 1-signal, 2-fakes
bdt_class  = [  0,   1,   2,   2]
bdt_dict = {0:'ditau', 1:'signal', 2:'fakes'}
FF_Types = ['wj','qcd','mc_top']

cmssw_base = os.getenv('CMSSW_BASE')
base_folder = '%s/src/IPcorrectionsRun3/FakeFactors'%(cmssw_base)

print('')
print('Testing ROOT-based interface ... ')
print('')
rootfilename='%s/data/FF_closure_%s.root'%(base_folder,args.channel)

ff_closure = FFclosure(filename=rootfilename)

for i in range(len(bdt_score)):    
    cat = bdt_dict[bdt_class[i]]
    print('BDT : class=%1i(%s)  score=%4.2f'%(bdt_class[i],
                                              cat,
                                              bdt_score[i]))
    for FF in FF_Types:
        nom = ff_closure.getCorrection(bdt_score[i],cat,FF)
        up = 2*nom - 1.
        down = 1.0
        if FF=='qcd':
            up = nom
            nom = 1.0
            down = 2.0 - nom
        print('  FF(%s) = %4.2f(nom)  %4.2f(up)  %4.2f(down)'%(FF,nom,up,down))

print('')
print('Testing json-based interface ... ')
print('')
jsonfilename='%s/JSON/FF_closure_%s.json'%(base_folder,args.channel)
cset = correctionlib.CorrectionSet.from_file(jsonfilename)
corr = cset['FF_closure']

fakeF = {}
fakeF_up = {}
fakeF_down = {}

for FF in FF_Types:
    
    fakeF[FF] = corr.evaluate(bdt_score,bdt_class,FF,'nom')
    fakeF_up[FF] = corr.evaluate(bdt_score,bdt_class,FF,'up')
    fakeF_down[FF] = corr.evaluate(bdt_score,bdt_class,FF,'down')
    
for i in range(len(bdt_score)):
    print('BDT : class=%1i  score=%4.2f'%(bdt_class[i],
                                          bdt_score[i]))

    for FF in FF_Types:
        print('  FF(%s) = %4.2f(nom)  %4.2f(up)  %4.2f(down)'%(FF,
                                                               fakeF[FF][i],
                                                               fakeF_up[FF][i],
                                                               fakeF_down[FF][i]
                                                               ))
