from flask import Flask,jsonify,request,Response
import pymysql
import requests
from __main__ import app

db = pymysql.connect("localhost", "root", "", "Farmers")

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