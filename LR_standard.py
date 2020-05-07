#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 13:25:50 2020

@author: danielbean
"""

# standard LR using statsmodels

import statsmodels.api as sm
import pandas as pd
import numpy as np


def analyse(factors, data, significance_level = 0.05, add_constant = True):
    X = data[factors]
    y = data['Endpoint Status']

    if add_constant:
        X = sm.add_constant(X)
        
    X = X.astype(float)
    
    #model = sm.OLS(y, X).fit() #linear regression
    model = sm.Logit(y, X).fit()
    params = model.params
    conf = model.conf_int()
    conf['OR'] = params
    conf.columns = ['Lower 95%CI', 'Upper 95%CI', 'OR']
    or_ci = np.exp(conf)
    or_ci = or_ci.round(2)
    or_ci['raw P-value'] = model.pvalues
    or_ci['Significant'] = or_ci['raw P-value'] < significance_level
    print(model.summary())
    print()
    print(or_ci)
    return or_ci

outs = pd.read_csv("output/outcomes_dataset_for_analysis.csv")
age_col = 'Age (per 10 years)'

# =============================================================================
# combine some comorbidities, rename some columns
# =============================================================================
outs['ACEi'] = outs['On ACE inhibitor']
outs['ARB'] = outs['On ARB']
outs['On ACEi or ARB'] = outs[['On ACE inhibitor', 'On ARB']].any(axis=1)
outs['Statin'] = outs['On Statin']
outs['Beta-blocker'] = outs['On Beta-blocker']
outs['HF or IHD'] = outs[['IHD', 'HF']].any(axis=1)


# =============================================================================
# run analysis
# =============================================================================

factors = ['On ACEi or ARB']
baseline = analyse(factors, outs)
baseline['Model'] = "Baseline"

factors = ['On ACEi or ARB',age_col, 'Male' ]
m1 = analyse(factors, outs)
m1['Model'] = "Model 1"


factors = ['On ACEi or ARB',age_col, 'Male', 'HTN' ]
m2 = analyse(factors, outs)
m2['Model'] = "Model 2"

#all comos
factors = ['On ACEi or ARB',age_col, 'Male', 'HTN', 'Diabetes', 'HF or IHD', 'CKD' ]
m3 = analyse(factors, outs)
m3['Model'] = "Model 3"


res = pd.concat([baseline, m1, m2, m3], axis=0)
res.to_csv("output/ACE2_LR_standard.csv")
