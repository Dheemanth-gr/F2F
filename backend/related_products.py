import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json

# dataset = pd.read_csv('data/Market_Basket_Optimisation.csv', header = None) 

#Transforming the list into a list of lists, so that each transaction can be indexed easier
# transactions = []
# for i in range(0, dataset.shape[0]):
#     transactions.append([str(dataset.values[i, j]) for j in range(0, 20)])

# print(transactions[0])

from apyori import apriori
# Please download this as a custom package --> type "apyori"
# To load custom packages, do not refresh the page. Instead, click on the reset button on the Console.

def related(transactions,item):

    item = item.lower()
    print(item)
    rules = apriori(transactions, min_support = 0.003, min_confidence = 0.2, min_lift = 3, min_length = 2)
    # Support: number of transactions containing set of times / total number of transactions
    # .      --> products that are bought at least 3 times a day --> 21 / 7501 = 0.0027
    # Confidence: Should not be too high, as then this wil lead to obvious rules

    #Try many combinations of values to experiment with the model. 

    #viewing the rules
    results = list(rules)
    print(results)
    results = pd.DataFrame(results)

    res = list(results['items'])
    print(res)
    d = {}
    for itemset in res:
        for i in itemset:
            if i=='nan':
                continue
            if i not in d:
                d[i] = set()
            for j in itemset:
                if j!=i and j!='nan':
                    d[i].add(j)
    #print(d)
    if item not in d:
        return json.dumps([])
    return json.dumps(list(d[item]))
                
#print(related('Soup'))