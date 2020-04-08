# ACEi Analysis
## NOTE
This schema and code are for the our [preprint](https://www.researchgate.net/publication/340261837_Treatment_with_ACE-inhibitors_is_not_associated_with_early_severe_SARS-Covid-19_infection_in_a_multi-site_UK_acute_Hospital_Trust?channel=doi&linkId=5e806057a6fdcc139c10467a&showFulltext=true) but
we are now also collecting:
* Ethnicity
* 14 day outcomes
* discharge date

And will use these in ongoing analysis. Schema and code will be updated here.

#TODO
* penalised LR in R

## Overview
Run logistic regressions for ACEi exposure and outcome. The starting point for this code assumes you have all the
outputs for the schema below for the manual annotation, structured data, MedCAT and DrugPipeline steps which can be as separate files as in the demo folder. Scripts
here will merge and analyse those separate files. Demo data is in /demo. This is entirely random data and is not derived
from any real data, it is only to represent the file formats.

## Schema for full analysis
Source is as used for our [preprint](https://www.researchgate.net/publication/340261837_Treatment_with_ACE-inhibitors_is_not_associated_with_early_severe_SARS-Covid-19_infection_in_a_multi-site_UK_acute_Hospital_Trust?channel=doi&linkId=5e806057a6fdcc139c10467a&showFulltext=true).
Whatever source you use should be validated on your dataset.

Sources:
* Structured
  * Data available in structured form in EHR or derived from that automatically (e.g. document created within date range)
* Manual
  * Manually coded by clinician
* MedCAT
  * Available [here](https://github.com/CogStack/MedCAT).
* DrugPipeline
  * Available [here](https://github.com/dbeanm/DrugPipeline).

Variable | type | Notes | Source
--- | --- | --- | ---
Age | int | Age at sx, converted to 10 year increments for regression | Structured |
Male | bool | | Structured |
hypertension | bool | history of hypertension | MedCAT |
diabetes | bool | history of diabetes | MedCAT |
ischaemic heart disease or heart failure | bool | history of ischaemic heart disease or heart failure | MedCAT |
On NSAID | bool | Medication group 1: presence in Orders or Clinical Notes of the following Ibuprofen and all NSAID (e.g. Diclofenac, Naproxen). TRUE if any of these taken in study period | DrugPipeline |
On ACE inhibitor | bool | Medication group 2: presence in Orders or Clinical Notes of the following drugs Ramipril, Perindopril, Lisinopril, Enalapril, Captopril, Quinapril, Imidapril, Fosinopril, Trandolapril. TRUE if any of these taken in study period | DrugPipeline |
On ARB | bool | Medication group 3: presence in Orders or Clinical Notes of the following drugs Candesartan, Irbesartan, Losartan, Olmesartan, telmisartan, Valsartan. TRUE if any of these taken in study period | DrugPipeline |
Sx Date | date | | Manual |
ITU Date | date | | Manual |
Death Date | date | | Manual |
Medication order data in study period | bool | This is from structured data on in-hospital medication orders | Structured |
Any document in study period | bool | Discharge summary, A&E GP letter, clinical note | Structured |
Any clinical notes in study period | bool | Clinical notes only | Structured |



## Demo data
Files in /demo are random data designed to follow the same formats as DrugPipeline and MedCAT outputs.
The MedCAT output is already aggregated to patient level as this step is performed by our trained
MedCAT model (the pt2cuis.json output file).
