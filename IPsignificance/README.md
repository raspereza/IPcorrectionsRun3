# IP significance corrections

## Installation

Login to lxplus machine. It is assumed that you have already installed `CMSSW_14_1_0_pre4` or higher versions of the `CMSSW` package. Execute the following commands:

```
cd ${CMSSW_BASE}/src
cmsenv
git clone https://github.com/raspereza/IPcorrectionsRun3.git
cd IPcorrectionsRun3/IPsignificance
scramv1 b 
```

## RooT files with scale factors

The scale factors are stored in the form of RooT histograms in files located in the folder
`${CMSSW_BASE}/src/IPcorrectionsRun3/IPsignificance/data`. Currently, there are in total 8
RooT files with scale factors: 2 lepton flavours (electron or muon) x 2 lepton types (prompt lepton or lepton stemming from tau decay) x 2 Run3 eras (2022 or 2023). The name of each RooT file reflects
the era, lepton flavour and type of lepton (prompt lepton or lepton from tau decay), for which 
corrections are derived. For example, file `SF_PromptMu_Run3_2022.root` contains scale factors derived for prompt muons in the 2022 dataset, whereas file `SF_TauE_Run3_2023.root` contains scale factors derived for electrons from tau decays in the 2023 dataset. The scale factors are derived as a function of lepton pT for three eta bins:
* |eta| < 1.0
* 1.0 < |eta| < 1.6
* 1.6 < |eta| < 2.1 (2.4) for electrons (muons)

The scale factors are stored in the form of RooT functions (TF1 objects), corresponding to three measurement bins in eta and three options: central values, up systematic variation, and down systematic variation. Functions are named according to the following mnemonic `fitFunc_binEta${bin}_${opt}`, where 
* `${bin}=1` corresponds to |eta| < 1.0;
* `${bin}=2` corresponds to 1.0 < |eta| < 1.6;
* `${bin}=3` corresponds 1.6 < |eta| < 2.1 (2.4) for electrons (muons);
and
* `${opt}={central,up,down}`.

Interface to scale factors is implemented in the script `${CMSSW_BASE}/src/IPcorrectionsRun3/IPsignificance/python/ScaleFactor.py`

## Testing scale factors

The scale factors can be tested with the script `${CMSSW_BASE}/src/IPcorrectionsRun3/IPsignificance/scripts/TestSFs.py` which takes two input parameters
* `--era` - era, available options: Run3_2022, Run3_2023; 
* `--lepton` - lepton type, available options: PromptE, PromptMu, TauE, TauMu.

For instance, running script with the following input parameters:
```
cd ${CMSSW_BASE}/src/IPcorrectionsRun3/IPsignificance
./scripts/TestSFs.py --era Run3_2022 --lepton PromptMu
```
will print out central values of scale factors along with up/down variations for prompt muons as measured in the 2022 dataset for eta = [0.2,0.8,1.4,2.0] and pt = [25,30,35,40,50,60,80] GeV.


## ROOT to Correctionlib JSON

To setup the environment, one can use `CMSSW` as mentioned above, or source a `LCG` environment just by doing
```bash
source setup.sh
```
from tha main repo.

Using **`scripts/CreateJSON.py`, one can dump the SFs from `ROOT` files to `correctionlib` JSON so that it can be used in analyses easily. One of the **`scripts/Configs`** is necessary to access some basic information. All one needs is a very simple command
```bash
python CreateJSON.py Configs/<config.yaml>
```
To validate the just cooked JSONs, using the same `pt` and `eta` values used for the `TestSFs.py`, one can easily load any of the JSONs, give the inputs and it will return the SFs. A simple example is given below
```bash
pt_points = [25, 30, 35, 40, 50, 60, 80, 120, 149, 200]
eta_points = [0.2, 0.4, 0.8, 1.2, 1.4, 1.9, 2.0, 2.3, 1.7, 1.5]

# checked for 2022_electron
>>> import correctionlib
>>> cset = correctionlib.CorrectionSet.from_file("IP_Significance_Correction_Run3_2022_electron.json")
>>> corr = cset["ipsig_correction"]

# Pronpt
>>> corr.evaluate(pt_points, eta_points, 0, "nom")
[1.00301875, 1.00301875, 1.00290466, 1.00731891, 1.0063184 ,1.06951105, 1.07543296, 1.08299383, 1.08490455, 1.02772482]
>>> corr.evaluate(pt_points, eta_points, 0, "up")
[1.01082933, 1.01082933, 1.00794623, 1.01363915, 1.01134386,1.07676091, 1.08522562, 1.09338219, 1.11015018, 1.05289229]
# tauDecay
>>> corr.evaluate(pt_points, eta_points, 1, "nom")
[0.97205955, 0.97205955, 0.97435849, 0.99535793, 0.99869251,1.01491711, 0.96754554, 0.73411427, 0.44924536, 0.64202417]
>>> corr.evaluate(pt_points, eta_points, 1, "down")
[0.9418946 , 0.9418946 , 0.95252165, 0.96970172, 0.95465019,0.94554706, 0.88493638, 0.59299283, 0.10652288, 0.38977125]
```
