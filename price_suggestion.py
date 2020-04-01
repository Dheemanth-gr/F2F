import numpy as np 
import pandas as pd
from statistics import mean

dataset = pd.read_csv('data/datafile.csv')

msp = {'Paddy':1815,'Jowar':2550,'Bajra':2000,'Maize':1760,'Ragi':3150,'Arhar':5800,'Moong':7050,'Urad':5700,'Cotton':5255,'Groundnut':5090,'Sunflower':5650,'Soyabean':3710,'Sesamum':6485,'Nigerseed':5940,'Wheat':1925,'Barley':1525,'Gram':4875,'Masur':4800,'Mustard':4425,'Safflower':5215,'Copra':9521,'Coconut':2571,'Jute':3950,'Sugarcane':275}

def clean(commodity):
    res = ""
    for c in commodity:
        if(c=='('):
            return res
        else:
            res += c
    return res
    
for ind in dataset.index: 
    dataset['commodity'][ind] = clean(dataset['commodity'][ind])
#print(dataset)


def predict(state, district, commodity):
    prices = []
    for ind in dataset.index:
        if(dataset['state'][ind]==state and dataset['district'][ind]==district and dataset['commodity'][ind]==commodity):
            prices.append(dataset['modal_price'][ind])
    if(len(prices)==0):
        if(commodity in msp):
            return {'wpi':0,'msp':msp[commodity]}
        else:
            return {'wpi':0,'msp':0}
    else:
        if(commodity in msp):
            return {'wpi':mean(prices),'msp':msp[commodity]}
        else:
            return {'wpi':mean(prices),'msp':0}
            
#print(predict('Andhra Pradesh','Kurnool','Jowar'))
#print(predict('Haryana','Ambala','Tomato'))
#print(predict('Madhya Pradesh','Ratlam','Wheat'))
