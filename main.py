from flask import Flask, request,json
from flask_cors import CORS

import mysql.connector
import jwt

app = Flask(__name__)
CORS(app)

# Connect DataBase
conn = mysql.connector.connect(host='localhost', port="3306",user='suresh',password='suresh',database='test')
cursor = conn.cursor()

# Base Route
@app.route('/')
def index():
    return "Welcome to eCommerce REST API."

# CREAT USER
@app.route('/createUser',methods=["POST"])
def createUser():
    getInfo = json.loads(request.data)

    chk1 = ""
    chk2 = ""
    for row in getInfo:
        if row == "email":
            chk1 = getInfo[row]

        if row == "phone_number":
            chk2 = getInfo[row]

        if(chk1 != ""  and chk2 != ""):
            # Verification for Email Alredy Exist or not.
            query_string = "SELECT * FROM ecommerce_users WHERE email LIKE %s"
            cursor.execute(query_string, [str(chk1)])
            isEmail = cursor.fetchall()

            # Verification for Phone Number Alredy Exist or not.
            query_string = "SELECT * FROM ecommerce_users WHERE phone_number LIKE %s"
            cursor.execute(query_string, [str(chk2)])
            isPhnNum = cursor.fetchall()

            if(isEmail.__len__() == 1 and  isPhnNum.__len__() == 1):
                return { "status": 422, "response": { "data" : "User Already Exists with " + chk1 + " Email and " + chk2 + " Phone_number." } }
            elif (isEmail.__len__() == 1):
                return { "status": 422, "response": { "data" :  "User Already Exists with " + chk1 + " Email." } }
            elif (isPhnNum.__len__() == 1):
                return { "status": 422, "response": { "data" : "User Already Exists with " + chk2  + " Phone_number."} }
            else:
                print("getInfo : ",getInfo)
                sql = "INSERT INTO `ecommerce_users` (`id`,`username`, `password`, `email`, `phone_number`, `address`, `photo`) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                data = ("NULL",getInfo['username'], getInfo['password'], getInfo['email'],getInfo['phone_number'], getInfo['address'], getInfo['photo'])

                cursor.execute(sql, data)
                conn.commit()

                return { "status": 200,"response": { "data" :  "New User added Successfully."} }

# USER LOGIN
@app.route('/userLogin',methods=["GET"])
def userLogin():
    getInfo = json.loads(request.data)
    print("getInfo",getInfo)

    query_string = "SELECT * FROM ecommerce_users WHERE email LIKE %s AND password LIKE %s"
    cursor.execute(query_string, [str(getInfo['email']), str(getInfo['password'])])
    resp = cursor.fetchall()

    if(resp.__len__() > 0):
        payload_data = {
            "username": str(getInfo['email']),
            "password": str(getInfo['password'])
        }
        return { "status-code": 200, "data": { "auth_token": jwt.encode(payload=payload_data, key='my_super_secret') }}
    else:
        return { "status": 401, "response": {"data": "Invalid User Credentials." }}

# GET USER
@app.route('/getUserInfo',methods=["GET"])
def getUserInfo():
    selectquery = "SELECT * FROM `ecommerce_users`"
    cursor.execute(selectquery)

    records = cursor.fetchall()

    result_list = []
    for info in records:
        result_list.append({"id" : info[0], "username" : info[1], "password": info[2], "email" : info[3],"phone_number" : info[4],"address" : info[5],"photo" : str(info[6])})

    return result_list

# UPDATE USER
@app.route('/updateUser',methods=["POST"])
def updateUser():
    getInfo = json.loads(request.data)

    # Get Query Params Values
    queryParam = request.args.get("id", type=str)

    sql = "UPDATE `ecommerce_users` SET `username` = %s, `password` = %s,`email` = %s,`phone_number` = %s,`address` = %s,`photo` = %s WHERE `ecommerce_users`.`id` = %s"
    data = (getInfo['username'], getInfo['password'], getInfo['email'], getInfo['phone_number'], getInfo['address'],getInfo['photo'],queryParam)

    cursor.execute(sql, data)
    conn.commit()

    return "User Info Updated Successfully."

# Running Port
app.run(port=8000)
cursor.close()
conn.close()