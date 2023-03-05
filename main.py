from flask import Flask, request,json
from flask_cors import CORS

import mysql.connector
import jwt

app = Flask(__name__)
CORS(app)

# Connect DataBase
conn = mysql.connector.connect(host='localhost', port="3306",user='suresh',password='suresh',database='ecommerce')
cursor = conn.cursor()

# Base Route
@app.route('/')
def index():
    return "Welcome to eCommerce REST API."

# ------------------------------------------------------------  USERS ----------------------------------------------------------------------------------

# CREAT USER
@app.route('/createUser',methods=["POST"])
def createUser():
    getInfo = json.loads(request.data)

    chk1 = ""
    chk2 = ""
    for row in getInfo:
        if row == "email":
            chk1 = getInfo[row]

        if row == "password":
            chk2 = getInfo[row]

        if(chk1 != ""  and chk2 != ""):
            # Verification for Email Alredy Exist or not.
            query_string = "SELECT * FROM users WHERE email LIKE %s"
            cursor.execute(query_string, [str(chk1)])
            isEmail = cursor.fetchall()

            # Verification for Phone Number Alredy Exist or not.
            query_string = "SELECT * FROM users WHERE password LIKE %s"
            cursor.execute(query_string, [str(chk2)])
            isPwd = cursor.fetchall()

            if(isEmail.__len__() == 1 and  isPwd.__len__() == 1):
                return { "status": 422, "response": { "data" : "User Already Exists with " + chk1 + " Email and " + chk2 + " Password." } }
            elif (isEmail.__len__() == 1):
                return { "status": 422, "response": { "data" :  "User Already Exists with " + chk1 + " Email." } }
            elif (isPwd.__len__() == 1):
                return { "status": 422, "response": { "data" : "User Already Exists with " + chk2  + " Password."} }
            else:
                print("getInfo : ",getInfo)
                sql = "INSERT INTO `users` (`id`,`username`, `email`,`password`) VALUES (%s, %s, %s, %s)"
                data = ("NULL",getInfo['username'], getInfo['email'], getInfo['password'])

                cursor.execute(sql, data)
                conn.commit()

                return { "status": 200,"response": { "data" :  "New User added Successfully."} }

# USER LOGIN
@app.route('/userLogin',methods=["GET"])
def userLogin():
    getInfo = json.loads(request.data)
    print("getInfo",getInfo)

    query_string = "SELECT * FROM users WHERE email LIKE %s AND password LIKE %s"
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
    selectquery = "SELECT * FROM `users`"
    cursor.execute(selectquery)

    records = cursor.fetchall()

    result_list = []
    for info in records:
        result_list.append({"id" : info[0], "username" : info[1], "email" : info[2],"password": info[3]})

    return result_list

# UPDATE USER
@app.route('/updateUser',methods=["POST"])
def updateUser():
    getInfo = json.loads(request.data)

    # Get Query Params Values
    queryParam = request.args.get("id", type=str)

    sql = "UPDATE `users` SET `username` = %s, `email` = %s,`password` = %s WHERE `users`.`id` = %s"
    data = (getInfo['username'], getInfo['email'], getInfo['password'],int(queryParam))

    cursor.execute(sql, data)
    conn.commit()

    return "User Info Updated Successfully."

# ------------------------------------------------------------  PRODUCTS  ----------------------------------------------------------------------------------

# GET Products
@app.route('/getProducts',methods=["GET"])
def getProducts():
    selectquery = "SELECT * FROM `products`"
    cursor.execute(selectquery)

    records = cursor.fetchall()

    result_list = []
    for info in records:
        result_list.append({"id" : info[0], "productname" : info[1], "price": info[2], "quantity" : info[3]})
    return result_list
    # if(result_list.__len__() > 0):
    #     return { "status": 200, "data":  result_list}
    # else:
    #     return { "status": 400, "data": {}}

# Running Port
app.run(port=8000)
cursor.close()
conn.close()