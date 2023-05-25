from flask import Flask
from pymongo import MongoClient
from flask.json import JSONEncoder
import json
from bson import json_util
from flask_cors import CORS

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        return json.JSONEncoder.default(obj)



def parse_json(data):
    return json.loads(json_util.dumps(data))


app = Flask("ReBoot")
# app.json_encoder = CustomJSONEncoder

CORS(app)

with open('app_main/config.json','r') as c:
    params = json.load(c)['params']

production = True

if production == True:
    db_uri = params['databases']['cloud']
else:
    db_uri = params['databases']['local']

app.config['SECRET_KEY'] = params['secrets']
app.config['MONGO_URI'] = db_uri



from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day"],
    storage_uri=db_uri
)


mongodb_client = MongoClient(db_uri)
db = mongodb_client[params["databases"]["db_token"]]


from app_main import api
from app_main import auth
from app_main import mailer
