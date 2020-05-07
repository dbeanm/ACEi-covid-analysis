# ACEi Analysis
## NOTE
This schema and code are for the our [preprint](https://www.researchgate.net/publication/340261837_Treatment_with_ACE-inhibitors_is_not_associated_with_early_severe_SARS-Covid-19_infection_in_a_multi-site_UK_acute_Hospital_Trust?channel=doi&linkId=5e806057a6fdcc139c10467a&showFulltext=true) but
we have now changed:
* add Ethnicity to summary table
* add Statins
* 21 day outcomes
* add discharge date
* ACEi and ARB are combined
And will use these in ongoing analysis. Schema and code will be updated here. The original analysis from the preprint is the repo release v0.1.

## Overview
## Aim
Run logistic regressions for ACEi/ARB exposure and outcome.

## Summary
The starting point for this code assumes you have all the
outputs for the schema below. How you prepare this data depends on your access/resources/governance. Details of how we prepared this
data for our preprint are provided below but the code here assumes these files are prepared (manual annotation, structured data, MedCAT and DrugPipeline) which can be as separate files as in the demo folder. Scripts here will merge and analyse those separate files.
Demo data is in /demo. This is entirely random data and is not derived from any real data, it is only to represent the file formats.

If you do not need to replicate our full pipeline to prepare data from NLP etc., start from LR_standard.py.

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
  * For allergy detection v0.2+ needed

Variable | type | Notes | Source
--- | --- | --- | ---
Age | int | Age at sx, converted to 10 year increments for regression | Structured |
Male | bool | | Structured |
HTN | bool | history of hypertension | MedCAT |
Diabetes | bool | history of diabetes | MedCAT |
IHD | bool | history of ischaemic heart disease | MedCAT |
HF | bool | history of heart failure | MedCAT |
COPD | bool | History of COPD | MedCAT |
Asthma | bool | History of Asthma | MedCAT |
CKD | bool | History of CKD | MedCAT |
Stroke/TIA | bool | History of Stroke (hemorrhagic or ischaemic) or TIA | MedCAT |
On NSAID | bool | Presence in Orders or Clinical Notes. TRUE if any of these taken in study period | DrugPipeline |
On ACE inhibitor | bool | Presence in Orders or Clinical Notes. TRUE if any of these taken in study period | DrugPipeline |
On ARB | bool | Presence in Orders or Clinical Notes. TRUE if any of these taken in study period | DrugPipeline |
On Statin | bool |Presence in Orders or Clinical Notes. TRUE if any of these taken in study period | DrugPipeline |
On Beta blocker | bool | Presence in Orders or Clinical Notes. TRUE if any of these taken in study period | DrugPipeline |
Sx Date | date | | Manual |
ITU Date | date | | Manual |
Death Date | date | | Manual |
Medication order data in study period | bool | This is from structured data on in-hospital medication orders | Structured |
Any document in study period | bool | Discharge summary, A&E GP letter, clinical note | Structured |
Any clinical notes in study period | bool | Clinical notes only | Structured |

Note HF and IHD are combined for the regression.

## Drug groups
### NSAID
Ibuprofen and all NSAID (e.g. Diclofenac, Naproxen)

### ACEi
Ramipril, Perindopril, Lisinopril, Enalapril, Captopril, Quinapril, Imidapril, Fosinopril, Trandolapril

### ARB
Candesartan, Irbesartan, Losartan, Olmesartan, telmisartan, Valsartan

### Statin
Atorvastatin,
Fluvastatin,
Lovastatin,
Pravastatin,
Rosuvastatin,
Simvastatin,

### Beta blocker
Acebutolol,
Alprenolol,
Atenolol,
Betaxolol,
Bevantolol,
Bisoprolol,
Bopindolol,
Bupranolol,
Carteolol,
Carvedilol,
Celiprolol,
Cloranolol,
Epanolol,
Esatenolol,
Esmolol,
Labetalol,
Landiolol,
Levobunolol,
Mepindolol,
Metoprolol,
Nadolol,
Nebivolol,
Oxprenolol,
Penbutolol,
Pindolol,
Practolol,
Propranolol,
Sotalol,
Talinolol,
Tertatolol,
Timolol


## Demo data
Files in /demo are random data designed to follow the same formats as DrugPipeline and MedCAT outputs.
The MedCAT output is already aggregated to patient level as this step is performed by our trained
MedCAT model (the pt2cuis.json output file). This file also has our concept groupings applied (see below) so some CUI are replaced by group names e.g. "Any: Diabetes" meaning at least one of the specific concepts in our diabetes group was detected.

The demo data is very likely to give strange results, it's only there to show file formats and check that code runs.

## MedCAT comorbidities
We use concept groups to extract comorbidities with MedCAT. The groups used are in /demo:
* ACEi_medcat_concept_groups.json - all related concepts for each comorbidity
* ACEi_medcat_concept_groups_filter.json - concepts filtered by performance in our data - this is the definition used in the paper.
If we've provided a trained model, the filtered version is probably the version to use. If you're training your own model, start from the full list and filter it based on your own performance.
