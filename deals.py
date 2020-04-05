import json 

rprices = {"rice":34,"wheat":29,"atta":30,"gram dal":66,"tur dal":87,"urad dal":99,"moong dal":96,"masoor dal":68,"sugar":39,"milk":45,"groundnut oil":137,"mustard oil":118,"vanaspati":89,"soya oil":99,"sunflower oil":108,"palm oil":90,"gur":46,"tea":218,"salt":16,"potato":23,"onion":39,"tomato":22}

def get_discount(prodname, price):
    prodname = prodname.lower()
    list = []
    if(prodname in rprices and rprices[prodname]>price):
        #add to db
        list.append(int(((rprices[prodname]-price)/rprices[prodname])*100))
    return json.dumps(list)

print(get_discount('wheat',25)) # Returns a list with discount percentage if applicable, else empty list