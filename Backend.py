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

    inp={"table":"product","type":"insert","columns":["PRODID","PRODTITLE","PRODDESC","PRODTYPE","UPLOADTIME","OWNERID","PRICE","MAXQUANT","MINBUYQUANT"],"data":[str(prodid),json["title"],json["desc"],json["type"],"25-01-2020:10-18-16",json["ownerid"],json["price"],json["maxquant"],json["minbuyquant"]]}
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
    reviewid=1234
    json = request.get_json()
    inp={"table":"review","type":"insert","columns":["REVIEWID","REVIEWERID","PRODID","REVIEWDESC","REVIEWSTAR","REVIEWTIME","VERIFIED"],"data":[str(reviewid),json["reviewerid"],json["prodid"],json["reviewdesc"],json["reviewstar"],"25-01-2020:10-18-16",json["verified"]]}
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
    inp={"table":"image","type":"insert","columns":["IMAGEID","PRODID","IMAGENAME","IMAGEPATH","IMAGEX"],"data":[str(imageid),prodid,filename,path,ext]}
    send=requests.post('http://127.0.0.1:5000/api/db/write',json=inp)

    if(send.status_code == requests.codes.ok):
        os.makedirs(uploads_dir, exist_ok=True)
        file.save(os.path.join(uploads_dir, filename))
        return Response("1",status=200,mimetype="application/text")
    else:
        return Response("0",status=500,mimetype="application/text")

@app.route('/api/sub/<term>',methods=["GET"])
def submission(term):

    #inp={"table":"product","columns":["PRODTITLE"],"where":""}
    inp={"table":"product","columns":["PRODTITLE"],"where":"PRODTITLE LIKE '"+term+"%'"}
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