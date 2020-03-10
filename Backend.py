from flask import Flask,jsonify,request,Response
import os
import pymysql
import requests
from werkzeug.utils import secure_filename

db = pymysql.connect("localhost", "root", "", "Farmers")

app = Flask(__name__)

@app.route('/api/user', methods=['POST'])
def add_user():
    json = request.get_json()
    userid=1237

    if json["type"]=="farmer":
        table="FARMER"
        columns=["FARMID","FARMNAME","FARMPASS","FARMLOC"]
    elif json["type"]=="consumer":
        table="CONSUMER"
        columns=["CONSID","CONSNAME","CONSPASS","CONSLOC"]

    inp={"table":table,"type":"insert","columns":columns,"data":[str(userid),json["name"],json["pass"],json["loc"]]}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/product', methods=['POST'])
def add_product():
    json = request.get_json()
    prodid=1236

    inp={"table":"PRODUCT","type":"insert","columns":["PRODID","PRODTITLE","PRODDESC","PRODTYPE","UPLOADTIME","OWNERID","PRICE","MAXQUANT","MINBUYQUANT"],"data":[str(prodid),json["title"],json["desc"],json["type"],"25-01-2020:10-18-16",json["ownerid"],json["price"],json["maxquant"],json["minbuyquant"]]}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
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
    reviewid=1235
    json = request.get_json()
    inp={"table":"REVIEW","type":"insert","columns":["REVIEWID","REVIEWERID","PRODID","REVIEWDESC","REVIEWSTAR","REVIEWTIME","VERIFIED"],"data":[str(reviewid),json["reviewerid"],json["prodid"],json["reviewdesc"],json["reviewstar"],"25-01-2020:10-18-16",json["verified"]]}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/image/<prodid>', methods=['POST'])
def upload(prodid):

    #Accepts all files
    #If user uploads the same file again then a new file will not be created
    imageid=1240
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
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/sub/<term>',methods=["GET"])
def search(term):

    #inp={"table":"product","columns":["PRODTITLE"],"where":""}
    inp={"table":"PRODUCT","columns":["PRODTITLE"],"where":"PRODTITLE LIKE '"+term+"%'"}
    send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
    credential=send.content
    credential=eval(credential)
    result=[i[0] for i in credential]
    """
    result=[]
    for i in credential:
        if(i[0].startswith(term)):
            result.append(i[0])
    """
    return jsonify(result)

@app.route('/api/product/<prodid>',methods=["GET"])
def disp_product(prodid):

    inp={"table":"PRODUCT","columns":["PRODTITLE","PRODDESC","PRODTYPE","UPLOADTIME","OWNERID","PRICE","MAXQUANT","MINBUYQUANT"],"where":"PRODID="+prodid}
    send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
    credential=send.content
    credential=eval(credential)

    for l in range(0,len(credential)):
        inp={"table":"FARMER","columns":["FARMNAME","FARMLOC"],"where":"FARMID="+str(credential[l][4])}
        send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
        user=send.content
        user=eval(user)
        for i in user[0]:
            print(i)
            credential[l].append(i)

    for i in range(0,len(credential)):
        temp = {}
        temp["PRODTITLE"] = credential[i][0]
        temp["PRODDESC"] = credential[i][1]
        temp["PRODTYPE"] = credential[i][2]
        temp["UPLOADTIME"] = credential[i][3]
        temp["OWNERID"] = credential[i][4]
        temp["PRICE"] = credential[i][5]
        temp["MAXQUANT"] = credential[i][6]
        temp["MINBUYQUANT"] = credential[i][7]
        temp["FARMNAME"] = credential[i][8]
        temp["FARMLOC"] = credential[i][9]
        credential[i] = temp

    return jsonify(credential)

@app.route('/api/review/<prodid>',methods=["GET"])
def disp_review(prodid):

    inp={"table":"REVIEW","columns":["REVIEWID","REVIEWERID","REVIEWDESC","REVIEWSTAR","REVIEWTIME","VERIFIED"],"where":"PRODID="+prodid}
    send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
    credential=send.content
    credential=eval(credential)

    for l in range(0,len(credential)):
        inp={"table":"CONSUMER","columns":["CONSNAME","CONSLOC"],"where":"CONSID="+str(credential[l][1])}
        send=requests.get('http://127.0.0.1:5000/api/db/read',json=inp)
        user=send.content
        user=eval(user)
        for i in user[0]:
            print(i)
            credential[l].append(i)

    for i in range(0,len(credential)):
        temp = {}
        temp["REVIEWID"] = credential[i][0]
        temp["REVIEWERID"] = credential[i][1]
        temp["REVIEWDESC"] = credential[i][2]
        temp["REVIEWSTAR"] = credential[i][3]
        temp["REVIEWTIME"] = credential[i][4]
        temp["VERIFIED"] = credential[i][5]
        temp["CONSNAME"] = credential[i][6]
        temp["CONSLOC"] = credential[i][7]
        credential[i] = temp

    return jsonify(credential)

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