# Jet->tau fake factors for CP H->tautau analysis with early Run3 data

## Installation

Login to lxplus machine. It is assumed that you have already installed `CMSSW_14_1_0_pre4` or higher versions of the `CMSSW` package. Execute the following commands if you have not yet cloned repository [https://github.com/raspereza/IPcorrectionsRun3](https://github.com/raspereza/IPcorrectionsRun3) 

```
cd ${CMSSW_BASE}/src
cmsenv
git clone https://github.com/raspereza/IPcorrectionsRun3.git
cd IPcorrectionsRun3/FakeFactors
scramv1 b 
```

If this package is already present in your project area, pull the recent updates from the git repository

```
cd IPcorrectionsRun3
git pull
cd IPcorrectionsRun3/FakeFactors
scramv1 b 
```

## RooT-based interface to fake factors

The fake factors are derived as a continuous functions of tau candidate pT and binned in the following additional variables:

* number of jets (Njets): Njets=0, Njets=1,`Njets>=2;
* tau candidate pseudorapidity (eta): barrel (|eta|<1.48), endcap (1.48<|eta|<2.5);
* tau decay mode (DM): pi (DM=0), rho (DM=1), a1_1pr (DM=2), a1_3pr (DM=10).

The tau decay mode is aligned with the definition used in the CP H->tautau analysis. Six types of fake factors are provided.

* `qcd` : fake factor for QCD procces. Derived in the data sideband : same-sign leptons, isolation of muon > 0.05. 
* `wj` : fake factors for W+Jets process. Derived in data sideband: opposite-sign leptons, mT > 70 GeV, special BDT > 0.2 and n_bjets==0.
* `mc_wj` : fake factors for W+Jets procces derived from MC in the same sideband region as `wj`. Used for validation tests.
* `mc_top` : fake factors for top-pair events derived from MC in the signal region.
* `ss_antiiso` : fake factors to study extrapolation uncertainties from same-sign to opposite-sign region in the QCD fake factors. Derived in the same-sign region with antiisolated muon: 1.5<iso(mu)<0.5
* `os_antiiso` : fake factors to study extrapolation uncertainties from same-sign to opposite-sign region in the QCD fake factors. Derived in the opposite-sign region with antiisolated muon: 1.5<iso(mu)<0.5

The dependence of fake factors on the tau candidate pT is stored in the form of TF1 objects in the ROOT files located in the folder [`IPcorrectionsRun3/FakeFactors/data`](https://github.com/raspereza/IPcorrectionsRun3/tree/main/FakeFactors/data).

Currently, there are two sets of fake factors measured for mu+tau channel. The file `FF_Run3_mt_v1.root` contains fake factors measured without applying IP significance cut on muon to enhance statistics in the measurement regions. The file `FF_Run3_mt_v2.root` contains fake factors with applying cut on IP significance of muon, IPSig(mu)>1. It was verified that two sets of fake factors yield comparable results. The cut on IP significance of muon doesn't bias the measurement of scale factors.   

Interface for non-vectorised analysis is provided via class [`IPcorrectionsRun3/FakeFactors/python/FakeFactor.py`](https://github.com/raspereza/IPcorrectionsRun3/tree/main/FakeFactors/python/FakeFactor.py). The initialization of class is done by passing to constructor one keyword argument - the name of the RooT file with corrections:

```
import os
from IPcorrectionsRun3.FakeFactors.FakeFactor import FakeFactor
cmssw_base = os.getenv('CMSSW_BASE')
filename = '%s/src/IPcorrectionsRun3/FakeFactors/data/FF_Run3_mt_v2.root'%(cmssw_base)
ff_evaluator = FakeFactor(filename=filename)
```

The evaluation of fake factor is done calling method `getFF` which takes one float/double argument (tau candidate pt), whereas other parameters are passed as string keyword arguments: 

```
ff = ff_evaluator.getFF(pt,
                        eta='endcap',
                        dm='rho'
                        njets='njets0',
                        typ='qcd',
                        sys='nom')
```

The keyword arguments have the following meanings

* `eta` - tau candidate eta: `barrel`, `endcap`
* `dm` - decay mode : `pi`, `rho`, `a1_1pr`, `a1_3pr`;
* `njets` - number of jets: `njets0`, `njets1`, `njets2`;
* `type` - fake factor type: `qcd`, `wj`, `mc_wj`, `mc_top`, `ss_antiiso`, `os_antiiso`
* `sys` - central value (`nom`) and systematic variation (`up` or `down`).

## ROOT to Correctionlib JSON

To setup the environment, one can use `CMSSW` as mentioned above, or source a `LCG` environment just by doing
```
bash
source setup.sh
```
from the main repo.

Using [IPcorrectionsRun3/FakeFactors/scripts/CreateJSON.py`](https://github.com/raspereza/IPcorrectionsRun3/blob/main/Factors/scripts/CreateJSON.py), one converts from `ROOT` files to `correctionlib` JSON so that it can be used in the analyses based on columnwise approach. The script
is run with one argument: the name of the RooT file without extension. An example of executing script is given below

```
./CreateJSON.py --filename FF_Run3_mt_v2
```

The output json files are already stored in the folder [`IPcorrectionsRun3/FakeFactors/JSON`](https://github.com/raspereza/IPcorrectionsRun3/tree/main/FakeFactors/JSON)

## Correctionlib interface

The json-based interface to fake factors complies with the correctionlib package. The access to fake factors is illustrated with the following snippet of code :

```
import os
import correctionlib

cmssw_base = os.getenv('CMSSW_BASE')

jsonfilename='%s/src/IPcorrectionsRun3/FakeFactors/JSON/FF_Run3_mt_v2.json'%(cmssw_base)
cset = correctionlib.CorrectionSet.from_file(jsonfilename)
corr = cset['Fake_factors']

pt    = [ 20,  30,   40,  50]
eta   = [0.2, 1.7, -0.6, 2.2]
dm    = [  0,   1,    2,  10]
njets = [  0,   1,    2,   3]
FF = 'qcd'
ff = {}
for sys in ['nom','up','down']:
   ff[sys] = corr.evaluate(pt,eta,njets,dm,FF,sys)

print(ff['nom'],ff['up'],ff['down'])

```

The evaluator of correction set takes the following arguments:

* `pt` - column of tau candidate pt (double)
* `eta` - column of tau candidate eta (double)
* `njets` - column of number of jets (int or double)
* `dm` - column of decay mode (int): available options - 0 (pi), 1 (rho), 2 (a1_1pr), 10 (a1_3pr).
* `FF` - type of FF as defined above (string)
* `sys` - 'nom', 'up' and 'down': central value and up/down variations (string) 

Evaluator returns column of fake factors or their up/down variations depending on specified parameter `sys`. The output produced by the code should look like this:

```
[0.04811876 0.02036017 0.02413395 0.02477415] [0.0551879  0.02302126 0.02801975 0.03066327] [0.04104962 0.01769908 0.02024815 0.01888503]
```
 
For further details/information on the custom TF1-based and json-based access to fake factors please inspect script 
[IPcorrectionsRun3/FakeFactors/scripts/TestFakeFactors.py`](https://github.com/raspereza/IPcorrectionsRun3/blob/main/FakeFactors/scripts/TestFakeFactors.py).
