#! /usr/bin/env python3
# From ROOT file to Corectionlib JSON

import os
import re
import sys
import ROOT
import yaml

import correctionlib._core as core
import correctionlib.schemav2 as schema
#import correctionlib.JSONEncoder as JSONEncoder
from correctionlib import JSONEncoder

import json, jsonschema
import gzip

ff_labels = ['qcd','wj','mc_wj','mc_top','os_antiiso','ss_antiiso']
njets_labels = ['njets0','njets1','njets2']
eta_labels = ['endcap','barrel','endcap']
dm_dict = {
    'pi': 0,
    'rho': 1,
    'a1_1pr': 2,
    'a1_3pr': 10,
    }

etaBins = [-2.5,-1.48,1.48,2.5]
njetsBins = [-0.5,0.5,1.5,100.]

def buildPtDependence(ptr, ff, dm, njets, eta):
    objects = [key.GetName() for key in ptr.GetListOfKeys()]

    print(ff,dm,njets,eta)
    
    fit_nom  = f"fitFunc_{ff}_{dm}_{njets}_{eta}_nom"
    fit_form_nom   = ptr.Get(fit_nom)
    fit_nom_params = [fit_form_nom.GetParameter(i) for i in range(fit_form_nom.GetNpar())]
    
    fit_up   = f"fitFunc_{ff}_{dm}_{njets}_{eta}_up"
    fit_form_up   = ptr.Get(fit_up)
    fit_up_params = [fit_form_up.GetParameter(i) for i in range(fit_form_up.GetNpar())]

    fit_down = f"fitFunc_{ff}_{dm}_{njets}_{eta}_down"
    fit_form_down   = ptr.Get(fit_down)
    fit_down_params = [fit_form_down.GetParameter(i) for i in range(fit_form_down.GetNpar())]

    print(fit_nom_params)
#    print(fit_up_params)
#    print(fit_down_params)

    xmin = 20.
    xmax = 70.

    x = f"min(max(x, {xmin}), {xmax})"

    items = []
    
    value_nom = schema.Formula(
	nodetype="formula",
        expression=f"[0] + [1]*{x} + [2]*pow({x},2) + [3]*pow({x},3)",
        parameters=fit_nom_params,
        parser= "TFormula",
        variables= ['pt']
    )

    value_up = schema.Formula(
        nodetype="formula",
        expression=f"[0] + [1]*{x} + [2]*pow({x},2) + [3]*pow({x},3) + sqrt( [4] + [5]*{x} + [6]*pow({x},2) + [7]*pow({x},3) + [8]*pow({x},4) + [9]*pow({x},5) + [10]*pow({x},6))",
        parameters=fit_up_params,
        parser= "TFormula",
        variables= ['pt']
    )
    value_down = schema.Formula(
        nodetype="formula",
        expression=f"[0] + [1]*{x} + [2]*pow({x},2) + [3]*pow({x},3) - sqrt( [4] + [5]*{x} + [6]*pow({x},2) + [7]*pow({x},3) + [8]*pow({x},4) + [9]*pow({x},5) + [10]*pow({x},6))",
        parameters=fit_down_params,
        parser= "TFormula",
        variables= ['pt']
    )

    nom = schema.CategoryItem(
        key = 'nom', # syst
        value = value_nom,
    )
    items.append(nom)
    sysUp = schema.CategoryItem(
        key = 'up', # syst
        value = value_up,
    )
    items.append(sysUp)
    sysDown = schema.CategoryItem(
    	key = 'down', # syst
        value = value_down,
    )
    items.append(sysDown)
    
    data = schema.Category(
        nodetype='category',
        input='sys',
        content=items,
    )

    """
    for ff_x in ff_labels:
        for dm_x in dm_labels:
            for njets_x in njets_labels:
                for eta_x in eta_labels:
                    valueUp = value_nom
                    valueDown = value_nom
                    sysUp_name = '_%s_%s_stat_up'%(ff,dm,njets,eta)
                    sysDown_name = '%s_%s_stat_down'%(ff,dm,njets,eta)            
                    if ff==ff_x and dm==dm_x and njets==njets_x and eta==eta_x:
                        valueUp = value_up
                        valueDown = value_down
                    sysUp = schema.CategoryItem(
                        key = sysUp_name, # syst
                        value = valueUp,
                    )
                    sysDown = schema.CategoryItem(
    		        key = sysDown_name, # syst
                        value = valueDown,
                    )
                    data.append(sysUp)
                    data.append(sysDown)
    """
    return data

def buildEtaBins(ptr, ff, dm, njets):
    data_array = []
    for eta in eta_labels:
        data_array.append(buildPtDependence(ptr, ff, dm, njets, eta))

    data = schema.Binning(
        nodetype='binning',
        input='eta',
        edges=[-2.5,-1.48,1.48,2.5],
        content=data_array,
        flow='clamp',
    )
    return data

def buildNJetsBins(ptr, ff, dm):
    data_array = []
    for njets in njets_labels:
        data_array.append(buildEtaBins(ptr, ff, dm, njets))

    data = schema.Binning(
        nodetype='binning',
        input='njets',
        edges=[-0.5,0.5,1.5,100.5],
        content=data_array,
        flow='clamp',
    )
    return data

def buildDMCategories(ptr, ff):
    data_array = []
    for dm in dm_dict:
        cat_item = schema.CategoryItem(
            key=dm_dict[dm],
            value=buildNJetsBins(ptr, ff, dm),
        )
        data_array.append(cat_item)
        
    data = schema.Category(
        nodetype='category',
        input='dm',
        content=data_array,
    )
    return data
        
def buildFFSchema(ptr):

    data_array = []
    for ff in ff_labels:
        cat_item = schema.CategoryItem(
            key=ff,
            value=buildDMCategories(ptr, ff),
        )
        data_array.append(cat_item)
    
    data = schema.Category(
        nodetype='category',
        input='FFtype',
        content=data_array
    )
    
    return data
    

if __name__ == "__main__":

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-filename','--filename',dest='filename',default='FF_Run3_mt_v2')
    args = parser.parse_args()
    
    filename = args.filename
    cmssw_folder = os.getenv('CMSSW_BASE')
    basefolder = '%s/src/IPcorrectionsRun3/FakeFactors'%(cmssw_folder)
    rootFileName = '%s/data/%s.root'%(basefolder,filename)
    f = ROOT.TFile(rootFileName,'READ')
    
    name = f"Fake_factors"
    info = r"Fake factors for CP H->tautau analysis"
    inputs = [
        {'name': "pt",    'type': "real",   'description': "tau pT"},
        {'name': "eta",   'type': "real",   'description': "tau eta"},
        {'name': "njets", 'type': "real",   'description': "number of jets"},
        {'name': "dm",    'type': "int",    'description': "decay mode: 0:pi, 1:rho, 2:a1_1pr, 10:a1_3pr"},
        {'name': "FFtype",'type': "string", 'description': "FF type : qcd, wj, mc_wj, mc_top"},
        {'name': "sys",   'type': "string", 'description': "nom, up, down"}
    ]
    output = {'name': "ff", 'type': "real", 'description': "Fake factor"}
    
    cset = schema.CorrectionSet(
        schema_version=2,
        description="Fake factors",
        corrections=[
            schema.Correction(
                name=name,
                description=info,
                version=1,
                inputs=inputs,
                output=output,
                data=buildFFSchema(f),
            )
        ],
    )


    outPath = '%s/JSON'%(basefolder)
    if not os.path.exists(outPath):
        os.mkdir(outPath)
    else:
        print(f"{outPath} found")

    print(f">>> Writing {filename}...")
    JSONEncoder.write(cset, f"{outPath}/{filename}.json")
    
    print("Done ...")
