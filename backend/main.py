from flask import Flask,jsonify,request,Response,render_template
from flask_cors import CORS, cross_origin
import os
import requests
import pymysql
from werkzeug.utils import secure_filename
import price_suggestion as ps
import related_products as rp
import datetime

config = {
        'user': 'root',
        'password': '123',
        'host': 'db',
        'port': 3306,
        'database': 'F2F'
    }

HOST_ADDR="http://"+os.environ['HOST_IP']+":"+os.environ['HOST_PORT']

#db = pymysql.connect(**config)
#making db local to read_db and write_db functions

app = Flask(__name__)

@app.route('/', methods=['GET'])
@cross_origin(origin='*')
def testing():
    return "0"

def current_time():
    now = datetime.datetime.now()
    return now.strftime("%d-%m-%Y %H:%M:%S")

@app.route('/api/check', methods=['GET'])
@cross_origin(origin='*')
def check():
    json = request.get_json(force=True)

    inp={"table":json["table"],"columns":["*"],"where":json["where"]}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    if(len(data) > 0):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=204,mimetype="application/text")

@app.route('/api/deals/<num>', methods=['GET'])
@cross_origin(origin='*')
def deals(num):

    inp={"table":"DEALS","columns":["*"],"where":"PRODID>0 ORDER BY DISCOUNT_PERCENT DESC LIMIT "+num}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    result = []
    for deal in data:
        send=requests.get(HOST_ADDR+'/api/product/'+str(deal[1]))
        res=send.content
        res=eval(res)
        res["UNIT_PRICE"]=deal[2]
        res["DISCOUNT_PERCENT"]=deal[3]
        res['PRODID']=str(deal[1])
        result.append(res)

    return jsonify(result)

@app.route('/api/transactions', methods=['GET'])
@cross_origin(origin='*')
def transactions():

    inp={"table":"SALES","columns":["DISTINCT SALEID"],"where":""}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    result = []
    for trans in data:
        inp={"table":"SALES","columns":["PRODID"],"where":"SALEID = "+str(trans[0])}
        send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
        res=send.content
        res=eval(res)
        products=[]
        for prod in res:
            inp={"table":"PRODUCT","columns":["PRODTITLE"],"where":"PRODID = "+str(prod[0])}
            send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
            product=send.content
            product=eval(product)
            products.append(product[0][0])
        result.append(products)

    return jsonify(result)

@app.route('/api/related/<prodid>',methods=['GET'])
@cross_origin(origin='*')
def related_products(prodid):
    
    inp={"table":"PRODUCT","columns":["PRODTITLE"],"where":"PRODID = "+prodid}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    if len(data)==0:
        return "[]"
    send=requests.get(HOST_ADDR+'/api/transactions')
    transactions=send.content
    transactions=eval(transactions)
    #print(transactions)
    rel = rp.related(transactions,data[0][0])
    rel=eval(rel) 
    #print(rel)
    result = []
    products={prodid}
    for prod in rel:
        #print(prod)
        inp={"table":"PRODUCT","columns":["PRODID"],"where":"PRODTITLE LIKE '"+prod+"%'"}
        send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
        ids=send.content
        ids=eval(ids)
        for pid in ids:
            if str(pid[0]) not in products:
                products.add(str(pid[0]))
            else:
                continue
            send=requests.get(HOST_ADDR+'/api/product/'+str(pid[0]))
            d=send.content
            d=eval(d)
            d["PRODID"]=str(pid[0])
            del d["MAXQUANT"]
            del d["MINBUYQUANT"]
            result.append(d)

    return jsonify(result)

@app.route('/api/price', methods=['POST'])
@cross_origin(origin='*')
def predict_price():
    json = request.get_json()
    data = ps.predict(json["state"],json["district"],json["product"])
    #print(data)
    return jsonify(data)

@app.route('/api/GenId', methods=['GET'])
@cross_origin(origin='*')
def GenId():
    json = request.get_json(force=True)

    inp={"table":json["table"],"columns":["MAX("+json["column"]+")"],"where":""}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    if(data[0][0] != None):
        return Response(str(data[0][0]+1),status=200,mimetype="application/text")
    else:
        return Response("1",status=200,mimetype="application/text") 
@app.route('/api/login', methods=['POST'])
@cross_origin(origin='*')
def login():
    json = request.get_json(force=True)
    if(json["type"] == "consumer"):
        inp={"table":"CONSUMER","where":"CONSNAME = '"+json["name"]+"' AND CONSPASS = '"+json["passwd"]+"'"}
        json["type_id"]="CONSID"
        json["type_name"]="CONSNAME"
        json["loc_type"]="CONSLOC"
        
    else:
        inp={"table":"FARMER","where":"FARMNAME ='"+json["name"]+"' AND FARMPASS = '"+json["passwd"]+"'"}
        json["type_id"]="FARMID"
        json["type_name"]="FARMNAME"
        json["loc_type"]="FARMLOC"
    send=requests.get(HOST_ADDR+'/api/check',json=inp)

    if(send.status_code == requests.codes.ok):
        inp={"table":json["type"].upper(),"columns":[json["type_id"],json["loc_type"]],"where":json["type_name"]+" = '"+json["name"]+"'"}
        send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
        data=send.content.decode()
        id_=eval(data)
        return Response("successfully logged in,"+json["type"]+","+str(id_[0][0])+","+json["name"]+","+str(id_[0][1]),status=200,mimetype="application/text")
    else:
        return Response("error while loging in. check name and password again",status=201,mimetype="application/text")

@app.route('/api/user', methods=['POST'])
@cross_origin(origin='*')
def add_user():
    json = request.get_json(force=True)
    if(json["type"] == "consumer"):
        inp={"table":"CONSUMER","where":"CONSNAME = '"+json["name"]+"'"}
    else:
        inp={"table":"FARMER","where":"FARMNAME ='"+json["name"]+"'"}

    send=requests.get(HOST_ADDR+'/api/check',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("username already taken",status=201,mimetype="application/text")


    if json["type"]=="farmer":
        table="FARMER"
        columns=["FARMID","FARMNAME","FARMPASS","FARMLOC"]
    elif json["type"]=="consumer":
        table="CONSUMER"
        columns=["CONSID","CONSNAME","CONSPASS","CONSLOC"]
    
    inp={"table":table,"column":columns[0]}
    send=requests.get(HOST_ADDR+'/api/GenId',json=inp)
    userid=send.content
    userid=eval(userid)
    inp={"table":table,"type":"insert","columns":columns,"data":[str(userid),json["name"],json["passwd"],json["loc"]]}
    send=requests.post(HOST_ADDR+'/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("successfully created account",status=200,mimetype="application/text")
    else:
        return Response("error while creating. check name again",status=201,mimetype="application/text")

@app.route('/api/cart', methods=['PUT'])
@cross_origin(origin='*')
def update_cart():
    json = request.get_json()

    inp={"table":"PRODUCT","where":"PRODID = "+json["prodid"]+" AND MINBUYQUANT <="+json["quantity"]}
    send=requests.get(HOST_ADDR+'/api/check',json=inp)
    if(send.status_code != requests.codes.ok):
        return Response("Not buying minimum quantity",status=201,mimetype="application/text")

    inp={"table":"CART","where": "CONSID="+json["consid"]+" AND PRODID = "+json["prodid"]}
    send=requests.get(HOST_ADDR+'/api/check',json=inp)
    if(send.status_code != requests.codes.ok):
        return Response("Product not present in cart",status=201,mimetype="application/text")

    inp={"table": "CART","type": "update","columns": ["QUANTITY"],"data": [json["quantity"]],"where": "CONSID = "+json["consid"]+" AND PRODID = "+json["prodid"]}
    send=requests.post(HOST_ADDR+'/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/cart', methods=['DELETE'])
@cross_origin(origin='*')
def delete_cart():
    json = request.get_json()
    inp={"table": "CART","type": "delete","where": "CONSID = "+json["consid"]+" AND PRODID = "+json["prodid"]}
    send=requests.post(HOST_ADDR+'/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/product/<prodid>', methods=['DELETE'])
@cross_origin(origin='*')
def delete_product(prodid):
    inp={"table": "PRODUCT","type": "delete","where": "PRODID = "+str(prodid)}
    send=requests.post(HOST_ADDR+'/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/product', methods=['POST'])
@cross_origin(origin='*')
def add_product():
    json = request.get_json(force=True)
    inp={"table":"PRODUCT","column":"PRODID"}
    send=requests.get(HOST_ADDR+'/api/GenId',json=inp)
    prodid=send.content
    prodid=eval(prodid)
    inp={"table":"PRODUCT","type":"insert","columns":["PRODID","PRODTITLE","PRODDESC","PRODTYPE","UPLOADTIME","OWNERID","PRICE","MAXQUANT","MINBUYQUANT"],"data":[str(prodid),json["title"],json["desc"],json["type"],current_time(),json["ownerid"],json["price"],json["maxquant"],json["minbuyquant"]]}
    send=requests.post(HOST_ADDR+'/api/db/write',json=inp)

    price = int(json["price"])
    disc = ps.get_discount(json["title"],int(price))
    disc=eval(disc)
    #print(disc)
    if disc:
        disc=disc[0]
        #print(disc)
        inp={"table":"DEALS","column":"DEALID"}
        send=requests.get(HOST_ADDR+'/api/GenId',json=inp)
        dealid=send.content
        dealid=eval(dealid)
        inp={"table":"DEALS","type":"insert","columns":["DEALID","PRODID","NEWPRICE","DISCOUNT_PERCENT"],"data":[str(dealid),str(prodid),str(price),str(disc)]}
        send=requests.post(HOST_ADDR+'/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("Added Product to catalogue !,"+str(prodid)+","+str(prodid),status=200,mimetype="application/text")
    else:
        return Response("Error adding product ! Try again later",status=201,mimetype="application/text")
        
"""def old_add_product():
    json = request.get_json(force=True)
    inp={"table":"PRODUCT","column":"PRODID"}
    send=requests.get('http://127.0.0.1:5000/api/GenId',json=inp)
    prodid=send.content
    prodid=eval(prodid)
    inp={"table":"PRODUCT","type":"insert","columns":["PRODID","PRODTITLE","PRODDESC","PRODTYPE","UPLOADTIME","OWNERID","PRICE","MAXQUANT","MINBUYQUANT"],"data":[str(prodid),json["title"],json["desc"],json["type"],current_time(),json["ownerid"],json["price"],json["maxquant"],json["minbuyquant"]]}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)
    if(send.status_code == requests.codes.ok):
        return Response("Added Product to catalogue !,"+str(prodid)+","+str(prodid),status=200,mimetype="application/text")
    else:
        return Response("Error adding product ! Try again later",status=201,mimetype="application/text")    
    
"""


"""
{
	"table":"product",
	"type":"insert",
	"columns":["PRODID","PRODTITLE","PRODDESC","PRODTYPE","UPLOADTIME","OWNERID","PRICE","MAXQUANT","MINBUYQUANT"],
	"data":["1234","Organic Wheat","High Quality Organic Wheat","Wheat","25-01-2020:10-18-16","1234","50000","1000","10"]
}
"""

@app.route('/api/review', methods=['POST'])
@cross_origin(origin='*')
def add_review():
    inp={"table":"REVIEW","column":"REVIEWID"}
    send=requests.get(HOST_ADDR+'/api/GenId',json=inp)
    reviewid=send.content
    reviewid=eval(reviewid)
    json = request.get_json(force=True)
    inp={"table":"REVIEW","type":"insert","columns":["REVIEWID","REVIEWERID","PRODID","REVIEWDESC","REVIEWSTAR","REVIEWTIME","VERIFIED"],"data":[str(reviewid),json["reviewerid"],json["prodid"],json["reviewdesc"],json["reviewstar"],current_time(),json["verified"]]}
    send=requests.post(HOST_ADDR+'/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=201,mimetype="application/text")

@app.route('/api/cart', methods=['POST'])
@cross_origin(origin='*')
def add_cart():
    json = request.get_json(force=True)
    inp={"table":"CART","type":"insert","columns":["CONSID","PRODID","QUANTITY"],"data":[json["consid"],json["prodid"],json["quantity"]]}
    send=requests.post(HOST_ADDR+'/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/image/<imageid>', methods=['GET'])
@cross_origin(origin='*')
def get_image(imageid):

    inp={"table":"IMAGE","columns":["IMAGEPATH","IMAGENAME"],"where":"IMAGEID = "+imageid}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)

    if(len(data) > 0):
        return Response(data[0][0]+data[0][1],status=200,mimetype="application/text")
    else:
        return Response("0",status=204,mimetype="application/text")

@app.route('/api/buy/<consid>', methods=['GET'])
@cross_origin(origin='*')
def add_sale(consid):
    inp={"table":"CART","columns":["*"],"where":"CONSID="+consid}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    inp={"table":"SALES","column":"SALEID"}
    send=requests.get(HOST_ADDR+'/api/GenId',json=inp)
    saleid=send.content
    saleid=eval(saleid)
    for i in range(0,len(data)):
        inp={"table":"SALES","type":"insert","columns":["SALEID","CONSID","PRODID","QUANTITY","BUYTIME"],"data":[str(saleid),str(data[i][0]),str(data[i][1]),str(data[i][2]),current_time()]}
        send=requests.post(HOST_ADDR+'/api/db/write',json=inp)
        if(send.status_code != requests.codes.ok):
            return Response("0",status=500,mimetype="application/text")

    inp={"table":"CART","type":"delete","where":""}
    send=requests.post(HOST_ADDR+'/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/image/<prodid>', methods=['POST'])
@cross_origin(origin='*')
def upload(prodid):

    #Accepts all files
    #If user uploads the same file again then a new file will not be created
    inp={"table":"IMAGE","column":"IMAGEID"}
    send=requests.get(HOST_ADDR+'/api/GenId',json=inp)
    imageid=send.content
    imageid=eval(imageid)
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1]
    uploads_dir = "/images/"+prodid
    
    path=uploads_dir.replace("\\","/")
    ext=file_ext[1:]
    inp={"table":"IMAGE","type":"insert","columns":["IMAGEID","PRODID","IMAGENAME","IMAGEPATH","IMAGEX"],"data":[str(imageid),prodid,filename,path,ext]}
    send=requests.post(HOST_ADDR+'/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        os.makedirs(uploads_dir, exist_ok=True)
        file.save(os.path.join(uploads_dir, filename))
        return Response(str(imageid),status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/sub/<term>',methods=["GET"])
@cross_origin(origin='*')
def search(term):

    #inp={"table":"product","columns":["PRODTITLE"],"where":""}
    inp={"table":"PRODUCT","columns":["PRODTITLE","PRODID"],"where":"PRODTITLE LIKE '%"+term+"%'"}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    result=[[i[0],i[1]] for i in data]
    """
    result=[]
    for i in data:
        if(i[0].startswith(term)):
            result.append(i[0])
    """
    return jsonify(result)

@app.route('/api/search/<term>',methods=["GET"])
@cross_origin(origin='*')
def complete_search(term):

    #inp={"table":"product","columns":["PRODTITLE"],"where":""}
    inp={"table":"PRODUCT","columns":["PRODID"],"where":"PRODTITLE LIKE '%"+term+"%' OR PRODDESC LIKE '%"+term+"%'"}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    data=[i[0] for i in data]
    result=[]
    for i in data:
        send=requests.get(HOST_ADDR+'/api/product/'+str(i))
        d=send.content
        d=eval(d)
        d["PRODID"]=str(i)
        result.append(d)
    return jsonify(result)

@app.route('/api/product/<prodid>',methods=["GET"])
@cross_origin(origin='*')
def disp_product(prodid):

    inp={"table":"PRODUCT","columns":["PRODTITLE","PRODDESC","PRODTYPE","UPLOADTIME","OWNERID","PRICE","MAXQUANT","MINBUYQUANT"],"where":"PRODID="+prodid}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    data = data[0]

    #for l in range(0,len(data)):
    inp={"table":"FARMER","columns":["FARMNAME","FARMLOC"],"where":"FARMID="+str(data[4])}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    user=send.content
    user=eval(user)
    for i in user[0]:
        data.append(i)

    inp={"table":"IMAGE","columns":["IMAGEID","IMAGEPATH","IMAGENAME"],"where":"PRODID="+prodid}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    img=send.content
    img=eval(img)
    l = []
    for i in img:
        temp = {}
        temp["IMAGEID"] = i[0]
        temp["IMAGEPATH"] = i[1] + "/" + i[2]
        l.append(temp)
    data.append(l)

    #for i in range(0,len(data)):
    #print(data)
    #print(data[0])
    #print(data[6])

    temp = {}
    temp["PRODTITLE"] = data[0]
    temp["PRODDESC"] = data[1]
    temp["PRODTYPE"] = data[2]
    temp["UPLOADTIME"] = data[3]
    temp["OWNERID"] = data[4]
    temp["PRICE"] = data[5]
    temp["MAXQUANT"] = data[6]
    temp["MINBUYQUANT"] = data[7]
    temp["FARMNAME"] = data[8]
    temp["FARMLOC"] = data[9]
    temp["IMAGES"] = data[10]
    data = temp

    return jsonify(data)

@app.route('/api/cart/<consid>', methods=['GET'])
@cross_origin(origin='*')
def get_cart(consid):

    #inp={"table":"product","columns":["PRODTITLE"],"where":""}
    inp={"table":"CART","columns":["PRODID","QUANTITY"],"where":"CONSID ="+consid}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    result=[]
    for i in data:
        send=requests.get(HOST_ADDR+'/api/product/'+str(i[0]))
        d=send.content
        d=eval(d)
        d["BUY_Quanity"] = i[1]
        d["PRODID"]=str(i[0])
        del d["MAXQUANT"]
        del d["MINBUYQUANT"]
        result.append(d)
    return jsonify(result)


@app.route('/api/review/<prodid>',methods=["GET"])
@cross_origin(origin='*')
def disp_review(prodid):

    inp={"table":"REVIEW","columns":["REVIEWID","REVIEWERID","REVIEWDESC","REVIEWSTAR","REVIEWTIME","VERIFIED"],"where":"PRODID="+prodid}
    send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
    data=send.content
    data=eval(data)

    for l in range(0,len(data)):
        inp={"table":"CONSUMER","columns":["CONSNAME","CONSLOC"],"where":"CONSID="+str(data[l][1])}
        send=requests.get(HOST_ADDR+'/api/db/read',json=inp)
        user=send.content
        user=eval(user)
        for i in user[0]:
            #print(i)
            data[l].append(i)

    for i in range(0,len(data)):
        temp = {}
        temp["REVIEWID"] = data[i][0]
        temp["REVIEWERID"] = data[i][1]
        temp["REVIEWDESC"] = data[i][2]
        temp["REVIEWSTAR"] = data[i][3]
        temp["REVIEWTIME"] = data[i][4]
        temp["VERIFIED"] = data[i][5]
        temp["CONSNAME"] = data[i][6]
        temp["CONSLOC"] = data[i][7]
        data[i] = temp

    return jsonify(data)

@app.route('/api/db/write',methods=["POST"])
@cross_origin(origin='*')
def write_db():
    db = pymysql.connect(**config) 
    json = request.get_json(force=True)
    cur = db.cursor()

    if(json["type"]=="insert"):

        columns = json["columns"][0]
        data = "'"+json["data"][0]+"'"

        for iter in range(1,len(json["columns"])):
            columns = columns + "," +str(json["columns"][iter])
            data = data + ",'" + str(json["data"][iter])+"'"

        sql = "INSERT INTO "+json["table"]+"("+columns+") VALUES ("+data+")"
    elif(json["type"]=="delete"):

        if json["where"]!="":
            sql = "DELETE FROM "+json["table"]+" WHERE "+json["where"]
        else:
            sql = "DELETE FROM "+json["table"]

    elif(json["type"]=="update"):

            sql = "UPDATE "+json["table"]+" SET "+json["columns"][0]+"="+"'"+json["data"][0]+"'"
            for iter in range(1,len(json["columns"])):
                sql = sql + "," + json["columns"][iter]+"="+"'"+json["data"][iter]+"'"

            sql = sql + "WHERE "+json["where"]

    cur.execute(sql)
    db.commit()
    cur.close()
    db.close()
    return Response("1",status=200,mimetype="application/text")

"""
{
	"table":"farmer",
	"type":"insert",
	"columns":["FARMID","FARMNAME","FARMPASS","FARMLOC"],
	"data":["1234","Hello","password",""]
}
{
	"table":"farmer",
	"type":"delete",
	"where":""
}
"""

@app.route('/api/db/read',methods=["GET"])
@cross_origin(origin='*')
def read_db():
    db = pymysql.connect(**config) 
    json = request.get_json(force=True)
    cur = db.cursor()
    columns = json["columns"][0]
    
    for iter in range(1,len(json["columns"])):
        columns = columns + "," + json["columns"][iter]

    if json["where"]!="":
        sql = "SELECT "+columns+" FROM "+json["table"]+" WHERE "+json["where"]
    else:
        sql = "SELECT "+columns+" FROM "+json["table"]
    cur.execute(sql)
    results = cur.fetchall()
    results = list(map(list,results))
    cur.close()
    db.close()
    return Response(str(results),status=200,mimetype="application/text")

"""
{
	"table":"farmer",
	"columns":["FARMID","FARMNAME"],
	"where":""
}
"""

if __name__ == '__main__':
    app.debug=True
    app.run()
