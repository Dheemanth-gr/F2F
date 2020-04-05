import numpy as np 
import pandas as pd
from statistics import mean
import json

dataset = pd.read_csv('data/datafile.csv')

msp = {'paddy':1815,'jowar':2550,'bajra':2000,'maize':1760,'ragi':3150,'arhar':5800,'moong':7050,'urad':5700,'cotton':5255,'groundnut':5090,'sunflower':5650,'soyabean':3710,'sesamum':6485,'nigerseed':5940,'wheat':1925,'barley':1525,'gram':4875,'masur':4800,'mustard':4425,'safflower':5215,'copra':9521,'coconut':2571,'jute':3950,'sugarcane':275}

def clean(commodity):
    res = ""
    for c in commodity:
        if(c=='('):
            return res
        else:
            res += c
    return res
    
for ind in dataset.index: 
    dataset['commodity'][ind] = clean(dataset['commodity'][ind]).lower()
    dataset['state'][ind] = dataset['state'][ind].lower()
    dataset['district'][ind] = dataset['district'][ind].lower()
print(dataset)


def predict(state, district, commodity):
    state = state.lower()
    district = district.lower()
    commodity = commodity.lower()
    prices = []
    for ind in dataset.index:
        if(dataset['state'][ind]==state and dataset['district'][ind]==district and dataset['commodity'][ind]==commodity):
            prices.append(dataset['modal_price'][ind])
    if(len(prices)==0):
        if(commodity in msp):
            return json.dumps({'wpi':0,'msp':int(msp[commodity])})
        else:
            return json.dumps({'wpi':0,'msp':0})
    else:
        if(commodity in msp):
            return json.dumps({'wpi':int(mean(prices)),'msp':int(msp[commodity])})
        else:
            return json.dumps({'wpi':int(mean(prices)),'msp':0})
            
print(predict('Andhra Pradesh','Kurnool','Jowar'))
print(predict('Haryana','Ambala','Tomato'))
print(predict('Madhya Pradesh','Ratlam','Wheat'))
