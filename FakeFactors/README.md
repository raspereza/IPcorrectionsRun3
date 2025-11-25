
# Jet->tau fake factors for CP H->tautau analysis with early Run3 data (mu+tau and e+tau channels)

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

* `qcd` : fake factor for QCD procces. Derived in the data sideband : same-sign leptons, isolation of light lepton, 0.05 < iso(lepton) < 0.2 
* `wj` : fake factors for W+Jets process. Derived in data sideband: opposite-sign leptons, mT > 70 GeV, special BDT > 0.2 and n_bjets==0.
* `mc_wj` : fake factors for W+Jets procces derived from MC in the same sideband region as `wj`. Used for validation tests.
* `mc_top` : fake factors for top-pair events derived from MC in the signal region.

The dependence of fake factors on the tau candidate pT is stored in the form of TF1 objects in the ROOT files located in the folder [IPcorrectionsRun3/FakeFactors/data/Nov18](https://github.com/raspereza/IPcorrectionsRun3/tree/main/FakeFactors/data/Nov18). Four sets of fake factors are provided:

* `FF_Run3_mt_ipcut.root` : mu+tau channel, fake factors are measured with IP significance cut applied on muon.
* `FF_Run3_et_ipcut.root` : e+tau channel, fake factors are measured with IP significance cut applied on electron.
* `FF_Run3_mt_noipcut.root` : mu+tau channel, fake factors are measured without applying IP significance cut on muon.
* `FF_Run3_et_noipcut.root` : e+tau channel, fake factors are measured without applying IP significance cut applied on electron.

## ROOT to Correctionlib JSON

To setup the environment, one can use `CMSSW` as mentioned above, or source a `LCG` environment just by doing
```
bash
source setup.sh
```
from the main repo.

Using [IPcorrectionsRun3/FakeFactors/scripts/CreateJSON.py](https://github.com/raspereza/IPcorrectionsRun3/blob/main/Factors/scripts/CreateJSON.py), one converts from ROOT files to correctionlib JSON so that fake factors can be used in the analyses based on columnwise approach. The script
is run with two argument:
* --filename the name of the RooT file without extension;
* --with_eta : optional flag to introduce dependence of fake factors on eta.

An example of running:
```
./CreateJSON.py --filename Nov18/FF_Run3_mt_noipcut
```

Given limited statistics in determination regions, we recommend to use fake factors, where eta dependence is omitted. We also advice to use fake factors measured with the IP significance cut applied to leptons, as this cut is used in the nominal CP H->tautau analysis. 

The up-to-date output json files are already stored in the folder [IPcorrectionsRun3/FakeFactors/JSON/Nov18](https://github.com/raspereza/IPcorrectionsRun3/tree/main/FakeFactors/JSON/Nov18)
They encode fake factors, where dependence on eta is omitted. 

## Correctionlib interface

The json-based interface to fake factors complies with the correctionlib package. The access to fake factors is illustrated with the following snippet of code :

```
import os
import correctionlib

cmssw_base = os.getenv('CMSSW_BASE')

jsonfilename='%s/src/IPcorrectionsRun3/FakeFactors/JSON/Nov18/FF_Run3_mt_ipcut.json'%(cmssw_base)
cset = correctionlib.CorrectionSet.from_file(jsonfilename)
corr = cset['Fake_factors']

pt    = [ 20,  30,   40,  50]
dm    = [  0,   1,    2,  10]
njets = [  0,   1,    2,   3]
FF = 'qcd'
ff = {}
for sys in ['nom','up','down']:
   ff[sys] = corr.evaluate(pt,njets,dm,FF,sys)

print(ff['nom'],ff['up'],ff['down'])
```

The evaluator of correction set takes the following arguments:

* `pt` - column of tau candidate pt (double)
* `njets` - column of number of jets (int or double)
* `dm` - column of decay mode (int): available options - 0 (pi), 1 (rho), 2 (a1_1pr), 10 (a1_3pr).
* `FF` - type of FF : 'qcd', 'wj', 'mc_wj', 'mc_top'
* `sys` - 'nom', 'up' and 'down': central value and up/down variations (string) 

Evaluator returns column of fake factors or their up/down variations depending on specified parameter `sys`. The output produced by the code should look like this:

```
[0.04521284 0.03022546 0.02425191 0.0252838 ] [0.05160227 0.03205533 0.02795389 0.02921877] [0.03882341 0.0283956  0.02054992 0.02134883]

```
 
For further details/information on the json-based access to fake factors please inspect script 
[IPcorrectionsRun3/FakeFactors/scripts/TestFakeFactors.py](https://github.com/raspereza/IPcorrectionsRun3/blob/main/FakeFactors/scripts/TestFakeFactors.py).

