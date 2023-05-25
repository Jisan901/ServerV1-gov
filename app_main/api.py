from app_main import app, limiter, params, db, parse_json
import jwt
from flask import make_response,abort, request, jsonify
import datetime
from functools import wraps
from bson import ObjectId

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[1]
        if not token:
            return make_response({
                "message": "Authentication Token is missing!",
                "data": None,
                "error": "Unauthorized"
            }, 401)
        try:
            decoded = jwt.decode(token,params["jwt"],algorithms=["HS256"])
            if decoded is None:
                return make_response({
                "message": "Invalid Authentication token!",
                "data": None,
                "error": "Unauthorized"
            }, 401)
            if int(datetime.datetime.utcnow().timestamp()) > decoded["exp"]:
                return make_response({
                    "message": "Invalid Authentication token!",
                    "data": None,
                    "error": "Unauthorized"
                }, 401)
        except Exception as e:
            return make_response({
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500)

        return f(decoded, *args, **kwargs)

    return decorated

def admin_only(f):
    @wraps(f)
    def decorated(decoded,*args,**kwargs):
        if not decoded:
            return make_response({
                "message": "Invalid data!",
                "data": None,
                "error": "Invalid arguments"
            }, 401)
        try:
            user = decoded
            if user['role']!="admin":
                return make_response({
                    "message": "Invalid role!",
                    "data": None,
                    "error": "Invalid role"
                },401)
        except Exception as e:
            return make_response({
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500)
        
        return f(decoded,*args, **kwargs)
    return decorated
    
def verify_user(f):
    @wraps(f)
    def decorated(decoded,*args,**kwargs):
        if not decoded:
            return make_response({
                "message": "Invalid data!",
                "data": None,
                "error": "Invalid arguments"
            }, 401)
        try:
            user = parse_json(db.users.find_one({"email":decoded["email"]}))
            if not 'role' in user:
                return make_response({
                    "message": "Invalid role!",
                    "data": None,
                    "error": "Invalid role"
                },401)
        except Exception as e:
            return make_response({
                "message": "Something went wrong",
                "data": None,
                "error": str(e)
            }, 500)
        
        return f(user,*args, **kwargs)
    return decorated





@app.route("/")
def index():
    return ["server is running"]



@app.route("/user")
@token_required
@verify_user
def single_user(decoded):
    del decoded['password']
    return decoded




@app.route('/users')
@token_required
@verify_user
@admin_only
def all_users(decoded):
    return jsonify(parse_json(db.users.find({},{'password':0})))
    
    

@app.route('/changerole/<string:email>/<string:role>')
@token_required
@verify_user
@admin_only
def changerole(decoded,email,role):
    if email and role=="admin" or role=="user":
        return {"acknowledged":db.users.update_one({"email":email},{"$set":{
            "role": role
        }}).acknowledged}
        
    return {"acknowledged":None}
    
    





@app.route("/application",methods=['GET','POST'])
@token_required
@verify_user
def application(decoded):
    if request.method=="POST":
        body = request.json
        if "email" in body:
            if body['email']==decoded["email"]:
                body["status"]="pending"
                del decoded['password']
                body["user"]=decoded
                return {"id":parse_json(db.application.insert_one(body).inserted_id), "acknowledged":True}
            return make_response({
                "message":"Invalid email"
            },401)
        return make_response({
                "message":"forbidden email"
            },403)
    else:
        delta = parse_json(db.application.find({"email": decoded["email"]}))
        return delta
        
        
@app.route("/application/<string:oid>/<string:status>")
@token_required
@verify_user
@admin_only
def change_application_status(decoded,oid,status):
    if oid and status:
        result = db.application.update_one({"_id":ObjectId(oid)},{
            "$set":{
                "status":status
            }
        }).acknowledged
        return {"acknowledged":result}
    return {}
    


@app.route("/applications/<string:status>")
@token_required
@verify_user
@admin_only
def applications_for_admin(decoded,status):
    try:
        delta = parse_json(db.application.find({"status":status}))
        return delta
    except Exception as e:
        return make_response({"message":str(e)},500)
        
        
        
        
        
@app.route("/lookup")
@token_required
def lookup(decoded):
    return {"status":True}