import related_products as rp
import pandas as pd

dataset = pd.read_csv('data/Market_Basket_Optimisation.csv', header = None) 

#Transforming the list into a list of lists, so that each transaction can be indexed easier
transactions = []
for i in range(0, dataset.shape[0]):
    transactions.append([str(dataset.values[i, j]) for j in range(0, 20)])

print(rp.related(transactions,'Soup'))