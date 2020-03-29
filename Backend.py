from flask import Flask,jsonify,request,Response
import os
import pymysql
import requests
from werkzeug.utils import secure_filename

db = pymysql.connect("localhost", "root", "", "Farmers")

app = Flask(__name__)

def current_time():
    #TODO
    return "25-01-2020:10-18-16"

@app.route('/api/check', methods=['GET'])
def check():
    json = request.get_json()

    inp={"table":json["table"],"columns":["*"],"where":json["where"]}
    send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
    data=send.content
    data=eval(data)

    if(len(data) > 0):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=204,mimetype="application/text")

@app.route('/api/login', methods=['GET'])
def login():
    json = request.get_json()

    if(json["type"] == "consumer"):
        inp={"table":"CONSUMER","where":"CONSID ="+json["userid"]}
    else:
        inp={"table":"FARMER","where":"FAMRID ="+json["userid"]}
    send=requests.get('http://127.0.0.1:5000/api/check',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=204,mimetype="application/text")


@app.route('/api/GenId', methods=['GET'])
def GenId():
    json = request.get_json()

    inp={"table":json["table"],"columns":["MAX("+json["column"]+")"],"where":""}
    send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    print(data[0][0])
    if(data[0][0] != None):
        return Response(str(data[0][0]+1),status=200,mimetype="application/text")
    else:
        return Response("1",status=200,mimetype="application/text")

@app.route('/api/user', methods=['POST'])
def add_user():
    json = request.get_json()
    if json["type"]=="farmer":
        table="FARMER"
        columns=["FARMID","FARMNAME","FARMPASS","FARMLOC"]
    elif json["type"]=="consumer":
        table="CONSUMER"
        columns=["CONSID","CONSNAME","CONSPASS","CONSLOC"]
    
    inp={"table":table,"column":columns[0]}
    send=requests.get('http://127.0.0.1:5000/api/GenId',json=inp)
    userid=send.content
    userid=eval(userid)

    inp={"table":table,"type":"insert","columns":columns,"data":[str(userid),json["name"],json["pass"],json["loc"]]}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response(str(userid),status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/product', methods=['POST'])
def add_product():
    json = request.get_json()
    inp={"table":"PRODUCT","column":"PRODID"}
    send=requests.get('http://127.0.0.1:5000/api/GenId',json=inp)
    prodid=send.content
    prodid=eval(prodid)
    inp={"table":"PRODUCT","type":"insert","columns":["PRODID","PRODTITLE","PRODDESC","PRODTYPE","UPLOADTIME","OWNERID","PRICE","MAXQUANT","MINBUYQUANT"],"data":[str(prodid),json["title"],json["desc"],json["type"],current_time(),json["ownerid"],json["price"],json["maxquant"],json["minbuyquant"]]}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response(str(prodid),status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")
"""
{
	"table":"product",
	"type":"insert",
	"columns":["PRODID","PRODTITLE","PRODDESC","PRODTYPE","UPLOADTIME","OWNERID","PRICE","MAXQUANT","MINBUYQUANT"],
	"data":["1234","Organic Wheat","High Quality Organic Wheat","Wheat","25-01-2020:10-18-16","1234","50000","1000","10"]
}
"""

@app.route('/api/review', methods=['POST'])
def add_review():
    inp={"table":"REVIEW","column":"REVIEWID"}
    send=requests.get('http://127.0.0.1:5000/api/GenId',json=inp)
    reviewid=send.content
    reviewid=eval(reviewid)
    json = request.get_json()
    inp={"table":"REVIEW","type":"insert","columns":["REVIEWID","REVIEWERID","PRODID","REVIEWDESC","REVIEWSTAR","REVIEWTIME","VERIFIED"],"data":[str(reviewid),json["reviewerid"],json["prodid"],json["reviewdesc"],json["reviewstar"],current_time(),json["verified"]]}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response(str(reviewid),status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/cart', methods=['POST'])
def add_cart():
    json = request.get_json()
    inp={"table":"CART","type":"insert","columns":["CONSID","PRODID","QUANTITY"],"data":[json["consid"],json["prodid"],json["quantity"]]}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/buy', methods=['POST'])
def add_sale():
    inp={"table":"CART","columns":["*"],"where":""}
    send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    inp={"table":"SALES","column":"SALEID"}
    send=requests.get('http://127.0.0.1:5000/api/GenId',json=inp)
    saleid=send.content
    saleid=eval(saleid)
    for i in range(0,len(data)):
        inp={"table":"SALES","type":"insert","columns":["SALEID","CONSID","PRODID","QUANTITY","BUYTIME"],"data":[str(saleid),str(data[i][0]),str(data[i][1]),str(data[i][2]),current_time()]}
        send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)
        if(send.status_code != requests.codes.ok):
            return Response("0",status=500,mimetype="application/text")

    inp={"table":"CART","type":"delete","where":""}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response(str(saleid),status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/image/<prodid>', methods=['POST'])
def upload(prodid):

    #Accepts all files
    #If user uploads the same file again then a new file will not be created
    inp={"table":"IMAGE","column":"IMAGEID"}
    send=requests.get('http://127.0.0.1:5000/api/GenId',json=inp)
    imageid=send.content
    imageid=eval(imageid)
    file = request.files['file']
    filename = secure_filename(file.filename)
    file_ext = os.path.splitext(filename)[1]
    uploads_dir = os.path.join(os.getcwd(), 'Photos\\'+prodid)
    
    path=uploads_dir.replace("\\","/")
    ext=file_ext[1:]
    inp={"table":"IMAGE","type":"insert","columns":["IMAGEID","PRODID","IMAGENAME","IMAGEPATH","IMAGEX"],"data":[str(imageid),prodid,filename,path,ext]}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        os.makedirs(uploads_dir, exist_ok=True)
        file.save(os.path.join(uploads_dir, filename))
        return Response(str(imageid),status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/sub/<term>',methods=["GET"])
def search(term):

    #inp={"table":"product","columns":["PRODTITLE"],"where":""}
    inp={"table":"PRODUCT","columns":["PRODTITLE"],"where":"PRODTITLE LIKE '"+term+"%'"}
    send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
    data=send.content
    data=eval(data)
    result=[i[0] for i in data]
    """
    result=[]
    for i in data:
        if(i[0].startswith(term)):
            result.append(i[0])
    """
    return jsonify(result)

@app.route('/api/product/<prodid>',methods=["GET"])
def disp_product(prodid):

    inp={"table":"PRODUCT","columns":["PRODTITLE","PRODDESC","PRODTYPE","UPLOADTIME","OWNERID","PRICE","MAXQUANT","MINBUYQUANT"],"where":"PRODID="+prodid}
    send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
    data=send.content
    data=eval(data)

    for l in range(0,len(data)):
        inp={"table":"FARMER","columns":["FARMNAME","FARMLOC"],"where":"FARMID="+str(data[l][4])}
        send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
        user=send.content
        user=eval(user)
        for i in user[0]:
            print(i)
            data[l].append(i)

    for i in range(0,len(data)):
        temp = {}
        temp["PRODTITLE"] = data[i][0]
        temp["PRODDESC"] = data[i][1]
        temp["PRODTYPE"] = data[i][2]
        temp["UPLOADTIME"] = data[i][3]
        temp["OWNERID"] = data[i][4]
        temp["PRICE"] = data[i][5]
        temp["MAXQUANT"] = data[i][6]
        temp["MINBUYQUANT"] = data[i][7]
        temp["FARMNAME"] = data[i][8]
        temp["FARMLOC"] = data[i][9]
        data[i] = temp

    return jsonify(data)

@app.route('/api/review/<prodid>',methods=["GET"])
def disp_review(prodid):

    inp={"table":"REVIEW","columns":["REVIEWID","REVIEWERID","REVIEWDESC","REVIEWSTAR","REVIEWTIME","VERIFIED"],"where":"PRODID="+prodid}
    send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
    data=send.content
    data=eval(data)

    for l in range(0,len(data)):
        inp={"table":"CONSUMER","columns":["CONSNAME","CONSLOC"],"where":"CONSID="+str(data[l][1])}
        send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
        user=send.content
        user=eval(user)
        for i in user[0]:
            print(i)
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
def write_db():
    json = request.get_json()
    cur = db.cursor()

    if(json["type"]=="insert"):

        columns = json["columns"][0]
        data = "'"+json["data"][0]+"'"

        for iter in range(1,len(json["columns"])):
            columns = columns + "," + json["columns"][iter]
            data = data + ",'" + json["data"][iter]+"'"

        sql = "INSERT INTO "+json["table"]+"("+columns+") VALUES ("+data+")"
    elif(json["type"]=="delete"):

        if json["where"]!="":
            sql = "DELETE FROM "+json["table"]+" WHERE "+json["where"]
        else:
            sql = "DELETE FROM "+json["table"]

    cur.execute(sql)
    db.commit()
    cur.close()

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
def read_db():
    json = request.get_json()
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