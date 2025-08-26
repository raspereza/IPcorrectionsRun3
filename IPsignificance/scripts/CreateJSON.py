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



def IPSigPerSyst(ptr, ibin, variable):
    objects = [key.GetName() for key in ptr.GetListOfKeys()]
    
    fit_nom  = f"fitFunc_binEta{ibin}_central"
    fit_form_nom   = ptr.Get(fit_nom)
    fit_nom_params = [fit_form_nom.GetParameter(i) for i in range(fit_form_nom.GetNpar())]

    fit_up   = f"fitFunc_binEta{ibin}_up"
    fit_form_up   = ptr.Get(fit_up)
    fit_up_params = [fit_form_up.GetParameter(i) for i in range(fit_form_up.GetNpar())]

    fit_down = f"fitFunc_binEta{ibin}_down"
    fit_form_down   = ptr.Get(fit_down)
    fit_down_params = [fit_form_down.GetParameter(i) for i in range(fit_form_down.GetNpar())]

    h = fit_form_nom.GetHistogram()
    xmin = h.GetBinLowEdge(1)
    xmax = h.GetBinLowEdge(h.GetNbinsX()) + h.GetBinWidth(1)

    x = f"min(max(x, {xmin}), {xmax})"
    
    
    data = [
        schema.CategoryItem(
            key = 'nom', # syst
            value = schema.Formula(
                nodetype="formula",
                expression=f"[0] + [1]*{x} + [2]*pow({x},2)",
                parameters=fit_nom_params,
                parser= "TFormula",
                variables= [variable]
            ),
        ),
        schema.CategoryItem(
            key = 'up', # syst
            value = schema.Formula(
                nodetype="formula",
                expression=f"[0] + [1]*{x} + [2]*pow({x},2) + sqrt( [3] + [4]*{x} + [5]*pow({x},2) + [6]*pow({x},3) + [7]*pow({x},4) )",
                parameters=fit_up_params,
                parser= "TFormula",
                variables= [variable]
            ),
        ),
        schema.CategoryItem(
            key = 'down', # syst
            value = schema.Formula(
                nodetype="formula",
                expression=f"[0] + [1]*{x} + [2]*pow({x},2) - sqrt( [3] + [4]*{x} + [5]*pow({x},2) + [6]*pow({x},3) + [7]*pow({x},4) )",
                parameters=fit_down_params,
                parser= "TFormula",
                variables= [variable]
            ),
        ),
    ]        
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
                                'content' : IPSigPerSyst(fileDict[flavtype], i+1, 'pt')
                            } for i in range(len(etaBinEdges)-1)
                        ]
                    }
                } for flavtype, flavval in flavMap.items()
            ]
        }
    )    
    return data
    



def buildCorrection(era, lepFlav, flavMap, etaBinEdges, fileDict):
    name = f"ipsig_correction_{era}_{lepFlav}"
    info = "IP significance correction if IP_Sig > 1.0 is applied"
    inputs = [
        {'name': "pt",       'type': "real",   'description': "Reconstructed lepton pT"},
        {'name': "eta",      'type': "real",   'description': "Reconstructed lepton eta"},
        {'name': "flavor",   'type': "string", 'description': "prompt or decay from tau : 0 - prompt, 1 - taudecay"},
        {'name': "syst",     'type': "string", 'description': "nom, up or down"}
    ]
    output = {'name': "ipsig_correction", 'type': "real", 'description': "IP-Significance Correction"}
    
    cset = schema.CorrectionSet(
        schema_version=2,
        description="IP Sig Corr",
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
    cfg = loadcfg(cfgfile)

    era = cfg.get('era')
    lepFlav = cfg.get('leptonFlavor')
    etaBinEdges = cfg.get('etaBinEdges')
    fileDict = cfg.get('ROOTFiles')
    fileDict = {key: ROOT.TFile.Open(fileDict[key], "READ") for key in fileDict.keys()}
    flavTypes = list(fileDict.keys())
    flavMap = cfg.get('flavMap')
    outPath = cfg.get('outputPath')
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
