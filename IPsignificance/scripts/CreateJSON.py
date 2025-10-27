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

def loadcfg(cfgfile):
    cfg = None
    with open(cfgfile, "r") as f:
        cfg = yaml.safe_load(f)
    return cfg



def IPSigPerSyst(ptr, flavMap, flavtype, ibin, variable):
    objects = [key.GetName() for key in ptr.GetListOfKeys()]

    binDict = {
        1 : 3,
        2 : 2,
        3 : 1,
        4 : 1,
        5 : 2,
        6 : 3,
    }
    sysDict = {
        1 : 'etaLt1p0',
        2 : 'eta1p0to1p6',
        3 : 'etaGt1p6',
    }
    jbin = binDict[ibin]
    
    fit_nom  = f"fitFunc_binEta{jbin}_central"
    fit_form_nom   = ptr.Get(fit_nom)
    fit_nom_params = [fit_form_nom.GetParameter(i) for i in range(fit_form_nom.GetNpar())]

    fit_up   = f"fitFunc_binEta{jbin}_up"
    fit_form_up   = ptr.Get(fit_up)
    fit_up_params = [fit_form_up.GetParameter(i) for i in range(fit_form_up.GetNpar())]

    fit_down = f"fitFunc_binEta{jbin}_down"
    fit_form_down   = ptr.Get(fit_down)
    fit_down_params = [fit_form_down.GetParameter(i) for i in range(fit_form_down.GetNpar())]

    h = fit_form_nom.GetHistogram()
    xmin = h.GetBinLowEdge(1)
    xmax = 100.
#    xmax = h.GetBinLowEdge(h.GetNbinsX()) + h.GetBinWidth(1)


    x = f"min(max(x, {xmin}), {xmax})"

    data = []
    value_nom = schema.Formula(
	nodetype="formula",
        expression=f"[0] + [1]*{x} + [2]*pow({x},2)",
        parameters=fit_nom_params,
        parser= "TFormula",
        variables= [variable]
    )
    value_up = schema.Formula(
        nodetype="formula",
        expression=f"[0] + [1]*{x} + [2]*pow({x},2) + sqrt( [3] + [4]*{x} + [5]*pow({x},2) + [6]*pow({x},3) + [7]*pow({x},4) )",
        parameters=fit_up_params,
        parser= "TFormula",
        variables= [variable]
    )
    value_down = schema.Formula(
        nodetype="formula",
        expression=f"[0] + [1]*{x} + [2]*pow({x},2) - sqrt( [3] + [4]*{x} + [5]*pow({x},2) + [6]*pow({x},3) + [7]*pow({x},4) )",
        parameters=fit_down_params,
        parser= "TFormula",
        variables= [variable]
    )
    nom = schema.CategoryItem(
        key = 'nom', # syst
        value = value_nom,
    )
    data.append(nom)
    for l in sysDict:
        for flav in flavMap:            
            valueUp = value_nom
            valueDown = value_nom
            sysUp_name = '%s_%s_stat_up'%(flav,sysDict[l])
            sysDown_name = '%s_%s_stat_down'%(flav,sysDict[l])            
            if l==jbin and flav==flavtype:
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

    return data



    
def buildIPsigSchema(etaBinEdges, fileDict, flavMap):
    data = schema.Category.model_validate(
        {
            'nodetype': 'category',
            'input': "flavor",
            'content': [
                {
                    'key': flavval,
                    'value': {
                        'nodetype': 'binning',
                        'input': 'eta',
                        'edges': etaBinEdges,
                        'flow': 'clamp',
                        'content': [
                            {
                                'nodetype': 'category', # category:syst
                                'input': "syst",
                                'content' : IPSigPerSyst(fileDict[flavtype], flavMap, flavtype, i+1, 'pt')
                            } for i in range(len(etaBinEdges)-1)
                        ]
                    }
                } for flavtype, flavval in flavMap.items()
            ]
        }
    )    
    return data
    



def buildCorrection(era, lepFlav, flavMap, etaBinEdges, fileDict):
    name = f"ipsig_correction"
    info = r"IP significance correction for {lepFlav}"
    inputs = [
        {'name': "pt",       'type': "real",   'description': "Reconstructed lepton pT"},
        {'name': "eta",   'type': "real",   'description': "Reconstructed lepton eta"},
        {'name': "flavor",   'type': "int",    'description': "prompt or decay from tau : 0 - prompt, 1 - tauDecay"},
        {'name': "syst",     'type': "string", 'description': "nom, (prompt,tauDecay)__(up,down)"}
    ]
    output = {'name': "ipsig_correction", 'type': "real", 'description': "IP-Significance Correction"}
    
    cset = schema.CorrectionSet(
        schema_version=2,
        description="IP Significance Correction for electron and muon either as prompt or as tau decay product",
        corrections=[
            schema.Correction(
                name=name,
                description=info,
                version=1,
                inputs=inputs,
                output=output,
                data=buildIPsigSchema(etaBinEdges, fileDict, flavMap),
            )
        ],
    )
    return cset

def main(cfgfile):
    cmssw_folder = os.getenv('CMSSW_BASE')
    basefolder = '%s/src/IPcorrectionsRun3/IPsignificance'%(cmssw_folder)
    cfg = loadcfg(cfgfile)
    era = cfg.get('era')
    lepFlav = cfg.get('leptonFlavor')
    etaBinEdges = cfg.get('etaBinEdges')
    fileDict = cfg.get('ROOTFiles')
    fileDict = {key: ROOT.TFile.Open('%s/data/%s'%(basefolder,fileDict[key]), "READ") for key in fileDict.keys()}
    flavTypes = list(fileDict.keys())
    flavMap = cfg.get('flavMap')
    outPath = '%s/JSON'%(basefolder)
    if not os.path.exists(outPath):
        os.mkdir(outPath)
    else:
        print(f"{outPath} found")
    outFileBaseName = f"IP_Significance_Correction_Run3_{era}_{lepFlav}"

    corr = buildCorrection(era, lepFlav, flavMap, etaBinEdges, fileDict)

    print(f">>> Writing {outFileBaseName}...")
    JSONEncoder.write(corr, f"{outPath}/{outFileBaseName}.json")
    

if __name__ == "__main__":
    args = sys.argv
    assert len(args) >= 2; "config name is not given"
    cfgfile = sys.argv[1]
    main(cfgfile)
    print("Done ...")
