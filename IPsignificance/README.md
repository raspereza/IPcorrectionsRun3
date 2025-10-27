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
`${CMSSW_BASE}/src/IPcorrectionsRun3/IPsignificance/data`. Currently, there are in total 4
RooT files with scale factors: 2 lepton flavours (electron or muon) x 2 lepton types (prompt lepton or lepton stemming from tau decay). Scale factors are derived combining Run3_2022, Run3_2022EE, Run3_2023 and Run3_2023BPix datasets. The name of each RooT file reflects the lepton flavour and type of lepton (prompt lepton or lepton from tau decay), for which 
corrections are derived. For example, file `SF_PromptMu_Run3_2022-2023.root` contains scale factors derived for prompt muons, whereas file `SF_TauE_Run3_2022-2023.root` contains scale factors derived for electrons from tau decays. The scale factors are measured as a function of lepton pT for three eta bins:
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

## ROOT to Correctionlib JSON

To setup the environment, one can use `CMSSW` as mentioned above, or source a `LCG` environment just by doing
```bash
source setup.sh
```
from tha main repo.

Using **`scripts/CreateJSON.py`, one can dump the SFs from `ROOT` files to `correctionlib` JSON so that it can be used in analyses easily. One of the **`scripts/Configs`** is necessary to access some basic information. All one needs is a very simple command
```bash
./CreateJSON.py Configs/<config.yaml>
```

The json files for the combined 2022-2023 dataset are stored in the folder `${CMSSW_BASE}/src/IPcorrectionsRun3/IPsignificance/JSON`


## Testing scale factors

The scale factors can be tested with the script `${CMSSW_BASE}/src/IPcorrectionsRun3/IPsignificance/scripts/TestSFs.py` which takes as an input two parameter
* `--lepton` - lepton type, available options: PromptE, PromptMu, TauE, TauMu.
* `--pt` - transverse momentum of lepton.

For instance, running script with the following input parameters:
```
cd ${CMSSW_BASE}/src/IPcorrectionsRun3/IPsignificance
./scripts/TestSFs.py --lepton PromptMu --pt 40.
```
will print out central values of scale factors along with up/down variations for prompt muons for eta = [-1.9,-,0.8,1.4,2.0] using both TF1-based and correctionlib-based interfaces. 

The scale factors are measured independently in three eta bins and for two types of leptons: prompt and resulting from tau decays. Hence, there are six independent nuisance parameters controlling uncertainties in scale factors: .     
* prompt_etaLt1p0_stat
* prompt_eta1p0to1p6_stat
* prompt_etaGt1p6_stat
* tauDecay_etaLt1p0_stat
* tauDecay_eta1p0to1p6_stat
* tauDecay_etaGt1p6_stat

For further details/information on the custom TF1-based and correctionlib-based access to scale factors please inspect script 
`${CMSSW_BASE}/src/IPcorrectionsRun3/IPsignificance/scripts/TestSFs.py`.
