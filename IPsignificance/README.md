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

The scale factors are stored in finely pT-binned histograms (TH1 RooT objects), corresponding to three measurement bins in eta 
* histogran name `hfit_binEta1` : |eta| < 1.0
* histogran name `hfit_binEta2` : 1.0 < |eta| < 1.6
* histogran name `hfit_binEta3` : 1.6 < |eta| < 2.1 (2.4) for electrons (muons)

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


