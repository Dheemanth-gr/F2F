import numpy as np 
import pandas as pd
import json
import requests

response = requests.get('https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=579b464db66ec23bdd000001ede108b3318d4f2f70438ef63f85010b&format=json&offset=0&limit=10000')
data = eval(response.text)
dataset = pd.DataFrame(data['records'])

msp = {'paddy':1815,'jowar':2550,'bajra':2000,'maize':1760,'ragi':3150,'arhar':5800,'moong':7050,'urad':5700,'cotton':5255,'groundnut':5090,'sunflower':5650,'soyabean':3710,'sesamum':6485,'nigerseed':5940,'wheat':1925,'barley':1525,'gram':4875,'masur':4800,'mustard':4425,'safflower':5215,'copra':9521,'coconut':2571,'jute':3950,'sugarcane':275}

def clean(commodity):
    res = ""
    for c in commodity:
        if(c=='('):
            return res
        else:
            res += c
    return res

def modal_prices(pname,state):
    temp=dataset[dataset['commodity']==pname]
    return temp[temp['state']==state]

def rprices(pname):
    return dataset[dataset['commodity']==pname]['max_price']

def mean_price(dset):
    s=0
    l=0
    for ind in dset.index:
        s+=int(dset[ind])
        l+=1
    
    return s//l

def mean_df(dset):
    s=0
    l=0
    for ind in dset.index:
        s+=int(dset['modal_price'][ind])
        l+=1
    
    return s//l

for ind in dataset.index: 
    dataset['commodity'][ind] = clean(dataset['commodity'][ind]).lower()
    dataset['state'][ind] = dataset['state'][ind].lower()
    dataset['district'][ind] = dataset['district'][ind].lower()
#print(dataset)

def predict(state, district, commodity):
    state = state.lower().strip()
    district = district.lower().strip()
    commodity = commodity.lower().strip()
    prices = modal_prices(commodity,state)
    if(prices.empty==True):
        if(commodity in msp):
            return json.dumps({'wpi':0,'msp':int(msp[commodity])/100})
        else:
            return json.dumps({'wpi':0,'msp':0})
    else:
        if(commodity in msp):
            return json.dumps({'wpi':int(mean_df(prices)/100),'msp':int(msp[commodity])/100})
        else:
            return json.dumps({'wpi':int(mean_df(prices)/100),'msp':0})
            
#print(predict('Haryana','Ambala','Apple'))
#print(predict('Karnataka','Shimoga','Wheat'))

#rprices = {"rice":34,"wheat":29,"atta":30,"gram dal":66,"tur dal":87,"urad dal":99,"moong dal":96,"masoor dal":68,"sugar":39,"milk":45,"groundnut oil":137,"mustard oil":118,"vanaspati":89,"soya oil":99,"sunflower oil":108,"palm oil":90,"gur":46,"tea":218,"salt":16,"potato":23,"onion":39,"tomato":22}


def get_discount(prodname, price):
    #print(prodname)
    #print(price)
    prodname = prodname.lower().strip()
    list = []
    res=rprices(prodname)
    if(not res.empty):
        #add to db
        m_res=int(mean_price(rprices(prodname))/100)
        if m_res>price:
            list.append(int(((m_res-price)/m_res)*100))
    return json.dumps(list)