from app_main import app, db, parse_json, params, mongodb_client, limiter
from flask import abort, request, make_response
import datetime
import jwt

@app.route("/login",methods=['GET','POST'])
@limiter.limit("10 per day")
def login():
    if request.method == "POST":
        body = request.json
        isExist = parse_json(db.users.find_one({"email":body["email"]}))
        if isExist and "email" in isExist:
            if isExist['password']==body['password']:
                del isExist['password']
                
                isExist["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
                token = jwt.encode(isExist, params['jwt'], algorithm="HS256")
                
                return {"message":"login successful","token":token}
        return make_response({"message":"user not found"},404)
            
    else:
        return make_response({"message":"request not allowed !"},404)
        
        
@app.route("/signup",methods=['GET','POST'])
@limiter.limit("10 per day")
def signup():
    if request.method == "POST":
        body = request.json
        isExist = parse_json(db.users.find_one({"email":body["email"]}))
        
        if isExist and "email" in isExist:
            return {"massage":"email exist"}
        else:
            body['role'] = "user"
            data = db.users.insert_one(parse_json(body)).inserted_id
            
            del body['password']
            body["exp"] = datetime.datetime.utcnow() + datetime.timedelta(hours=12)
            token = jwt.encode(body, params['jwt'], algorithm="HS256")
            
            return {"message":"successfully account created","token":token}
        
    else:
        return make_response({"message":"request not allowed !"},404)
        




@app.route('/clear')
def cleardata():
    
    mongodb_client.drop_database('ReBootDB')
    mongodb_client.drop_database('limits')
    return ""