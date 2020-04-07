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


#ACEi  
factors = ['On ACE inhibitor']
m1a = analyse(factors, outs)
m1a['Model'] = "Baseline"
     
factors = ['On ACE inhibitor',age_col, 'Male' ]
m2a = analyse(factors, outs)
m2a['Model'] = "Model 1"

factors = ['On ACE inhibitor',age_col, 'Male', 'hypertension' ]
m4 = analyse(factors, outs)
m4['Model'] = "Model 2"

#all comos
factors = ['On ACE inhibitor',age_col, 'Male', 'hypertension', 'diabetes', 'ischaemic heart disease or heart failure' ]
m5 = analyse(factors, outs)
m5['Model'] = "Model 3"

#htn
factors = ['hypertension' ]
m1b = analyse(factors, outs)
m1b['Model'] = "Hypertension unadjusted"


factors = [age_col, 'Male', 'hypertension' ]
m2b = analyse(factors, outs)
m2b['Model'] = "Hypertension adjusted"


#ACEi + htn
#not in paper
factors = ['On ACE inhibitor', 'hypertension' ]     
m3 = analyse(factors, outs)
m3['Model'] = "ACE+HTN"


res = pd.concat([m1a, m1b, m2a, m2b, m3, m4, m5], axis=0)
res.to_csv("output/ACE2_LR_standard.csv")
