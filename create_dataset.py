#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 15:41:56 2020

@author: danielbean
"""

import pandas as pd
import json
from datetime import timedelta


identifier = 'Patient'
outs = pd.read_csv("demo/demographics_and_outcomes.csv")
meds_file = "demo/medications_reviewed.csv"
medcat_file = "demo/medcat_pt2cuis.json"
documents_file = "demo/documents.csv"
endpoint_window_days = 21
drug_pre_admission_window_days = 21
latest_data = pd.to_datetime("2020-03-31") # so we can detect pt whose 21 day window has not elapsed

# =============================================================================
# Preprocessing outcomes file
# =============================================================================
outs[identifier] = outs[identifier].astype(str)
date_cols = ['ITU Date', 'Sx Date', 'Death Date']
for d in date_cols:
    outs[d] = pd.to_datetime(outs[d], format='%d/%m/%Y')

window = timedelta(days=endpoint_window_days)
drug_window_pre = timedelta(days=drug_pre_admission_window_days)

outs['Endpoint'] = outs['Sx Date'] + window
outs['Medication inclusion start'] = outs['Sx Date'] - drug_window_pre
#stop looking for meds whenever an endpoint is reached
outs['Medication inclusion end'] = outs[['Endpoint', 'ITU Date', 'Death Date']].min(axis=1)
#outs['Medication inclusion end'] = outs['Endpoint']

outs['Death before endpoint'] = outs['Death Date'] <= outs['Endpoint']
outs['ITU before endpoint'] = outs['ITU Date'] <= outs['Endpoint']
outs['Endpoint Status'] = outs[['Death before endpoint', 'ITU before endpoint']].any(axis=1)

#remove patients who have not reached endpoint date yet
outs['Endpoint date reached'] = outs['Endpoint'] <= latest_data
outs['Endpoint outcome reached'] = outs[['Death before endpoint', 'ITU before endpoint']].any(axis=1)
outs['Ended'] = outs[['Endpoint date reached', 'Endpoint outcome reached']].any(axis=1)

outs.set_index(identifier, inplace=True)

#age
age_col = 'Age (per 10 years)'
outs[age_col] = outs['Age']/10
outs[age_col] = outs[age_col].astype(int)

# =============================================================================
# preprocess meds
# =============================================================================
meds = pd.read_csv(meds_file)
meds[identifier] = meds[identifier].astype(str)
meds_keep = ['Clinical Note', 'Medication', "A&E GP Letter", "Discharge Notification"]
meds = meds[meds['document_description'].isin(meds_keep)]
meds = meds[meds['review'].isna()]

prescriptions = pd.read_csv('demo/medication_orders.csv')
prescriptions[identifier] = prescriptions[identifier].astype(str)

has_med_order = prescriptions[identifier].unique()
outs['has_any_med_order'] = [x in has_med_order for x in outs.index]
print(sum(outs['has_any_med_order']),"/",outs.shape[0],'pt with outcomes have any medication order data')

p = prescriptions.set_index(identifier)
p = p.join(outs, how="inner")
p['updatetime date'] = pd.to_datetime(p['Date'], format='%d/%m/%Y')
p['doc_after_start'] = p['updatetime date'] >= p['Medication inclusion start']
p['doc_before_end'] = p['updatetime date'] <= p['Medication inclusion end']
p['doc_included'] = p[['doc_before_end', 'doc_after_start']].all(axis=1)
#this is to check that we have structured data coming through on this patient
#whether or not the order is for a drug we're interested in
any_med_order_included = p[p['doc_included'] == True].index.unique()
outs['has_any_med_order_in_window'] = [x in any_med_order_included for x in outs.index]

## medications within range from NLP
print("have", meds.shape[0],'positive mentions of meds')
print("for", meds.index.nunique(), 'patients')

meds.set_index(identifier, inplace=True)
meds = meds.join(outs, how='inner')

print("have", meds.shape[0],'positive mentions of meds after join to outcomes')
print("for", meds.index.nunique(), 'patients')

meds['updatetime date'] = pd.to_datetime(meds['Date'], format='%d/%m/%Y')
meds['doc_after_start'] = meds['updatetime date'] >= meds['Medication inclusion start']
meds['doc_before_end'] = meds['updatetime date'] <= meds['Medication inclusion end']
meds['doc_included'] = meds[['doc_before_end', 'doc_after_start']].all(axis=1)
meds['document_description'] = meds['document_description'].str.lower()
print(meds['doc_included'].sum(),"medication mentions in date range")


meds_included = meds[meds['doc_included'] == True].copy()
meds_included[identifier] = meds_included.index
meds_included.reset_index(drop=True, inplace=True)
gr = meds_included.groupby(['drug'])

drug_counts = gr[identifier].nunique().sort_values(ascending=False)
print("unique patients with drug mentions in window")
print(drug_counts)

on_drug = meds_included[identifier].unique()

# link outcome to meds
gr = meds_included.groupby('group')
for name, group in gr:
    n = "On " + name
    on = group[identifier].unique()
    outs[n] = [x in on for x in outs.index]
    n_mentions = group[identifier].value_counts()
    nn = "On " + name + " count"
    outs[nn] = n_mentions

# =============================================================================
# join to comorbidities from medcat
# =============================================================================
with open(medcat_file) as f:
    medcat = json.load(f)
    
outs['has_annotations'] = [x in medcat for x in outs.index]


## join to medcat
mct_ids = set(medcat.keys())
outs_ids = set(outs.index)
no_anns = outs_ids.difference(mct_ids)
print("medcat ids", len(mct_ids))
print("outcomes ids", len(outs_ids))
print("outcomes with medcat anns",len(outs_ids.intersection(mct_ids)))
print("outcomes with no annotations", len(no_anns))
print(no_anns)


comos_table = pd.read_csv("demo/ace2_comorbidities.csv")
g = comos_table.groupby('group')
cui_como = g['cui'].unique().to_dict()

rows = []

for p in medcat:
    p_cui = medcat[p] # new format is already onl those>= 2
    r = {identifier: p}
    for c in cui_como:
        r[c] = any([x in p_cui for x in cui_como[c]])
    rows.append(r)

## join to outcomes        
como_df = pd.DataFrame(rows)
como_df.set_index(identifier, inplace=True)


outs = outs.join(como_df, how='left')
comorb_list = comos_table['group'].unique().tolist()
outs[comorb_list] = outs[comorb_list].fillna(False)


# =============================================================================
# link to documents file
# =============================================================================
all_docs = pd.read_csv(documents_file)
all_docs[identifier] = all_docs[identifier].astype(str)
all_docs.set_index(identifier, inplace=True)
all_docs['updatetime'] = pd.to_datetime(all_docs['updatetime'], format='%d/%m/%Y')

docs_outs = all_docs.join(outs, how='inner')
docs_outs['doc_after_start'] = docs_outs['updatetime'] >= docs_outs['Medication inclusion start']
docs_outs['doc_before_end'] = docs_outs['updatetime'] <= docs_outs['Medication inclusion end']
docs_outs['doc_included'] = docs_outs[['doc_before_end', 'doc_after_start']].all(axis=1)
docs_outs['document_description'] = docs_outs['document_description'].str.lower()

docs_included = docs_outs[docs_outs['doc_included'] == True]
has_docs = docs_included.index.nunique()
has_cn = docs_included[docs_included['document_description'] == 'clinical note'].index.nunique()
has_status = outs.index.nunique()

print(has_docs,"/",has_status,"patients have any docs in window")
print(has_cn,"/",has_status,"patients have clinical notes")

id_with_doc = docs_included.index.unique()
id_with_doc_ever = docs_outs.index.unique()
id_with_cn = docs_included[docs_included['document_description'] == 'clinical note chunk'].index.unique()
outs['has_any_doc'] = [x in id_with_doc_ever for x in outs.index]
outs['has_any_doc_in_window'] = [x in id_with_doc for x in outs.index]
outs['has_clinical_note'] = [x in id_with_cn for x in outs.index]

# =============================================================================
# any data in window
# =============================================================================
outs['any_data_in_window'] = outs[['has_any_doc_in_window', 'has_any_med_order_in_window']].any(axis=1)
print("patients with any data in window")
print(outs['any_data_in_window'].value_counts())

# =============================================================================
# prepare dataset
# =============================================================================
## save a copy of everything before exclusions
outs.to_csv("output/outcomes_dataset_full.csv")
## exclusions
print("before exclusions,", outs.shape[0], 'patients total')
outs = outs[outs['Age'] > 1]
outs = outs[outs['has_annotations'] == True]
outs = outs[outs['any_data_in_window']]

#require study window ended
outs = outs[outs['Ended'] == True]
print("after exclusions,", outs.shape[0], 'patients total')

outs.to_csv("output/outcomes_dataset_for_analysis.csv")