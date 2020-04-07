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
#print(dataset)


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
            return json.dumps({'wpi':0,'msp':int(msp[commodity])/100})
        else:
            return json.dumps({'wpi':0,'msp':0})
    else:
        if(commodity in msp):
            return json.dumps({'wpi':int(mean(prices))/100,'msp':int(msp[commodity])/100})
        else:
            return json.dumps({'wpi':int(mean(prices))/100,'msp':0})
            
#print(predict('Andhra Pradesh','Kurnool','Jowar'))
#print(predict('Haryana','Ambala','Tomato'))
#print(predict('Madhya Pradesh','Ratlam','Wheat'))

rprices = {"rice":34,"wheat":29,"atta":30,"gram dal":66,"tur dal":87,"urad dal":99,"moong dal":96,"masoor dal":68,"sugar":39,"milk":45,"groundnut oil":137,"mustard oil":118,"vanaspati":89,"soya oil":99,"sunflower oil":108,"palm oil":90,"gur":46,"tea":218,"salt":16,"potato":23,"onion":39,"tomato":22}

def get_discount(prodname, price):
    print(prodname)
    print(price)
    prodname = prodname.lower()
    list = []
    if(prodname in rprices and rprices[prodname]>price):
        #add to db
        list.append(int(((rprices[prodname]-price)/rprices[prodname])*100))
    return json.dumps(list)
