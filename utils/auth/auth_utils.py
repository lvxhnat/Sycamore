import jwt
import os

import bcrypt
from pymongo import MongoClient 

from dotenv import load_dotenv
from datetime import datetime, timedelta 

load_dotenv()

def generate_token(username: str):
    payload = lambda x: {
        "exp": datetime.timestamp(datetime.now() + timedelta(hours = x)),
        "user": username,
            }
    access_token = jwt.encode(payload(int(os.environ['ACCESS_KEY_LIFETIME'])), os.environ['MASTER_SECRET_KEY'])
    return access_token

def verify_token(jwt_token: str):
    try:
        payload = jwt.decode(jwt_token, os.environ['DJANGO_SECRET_KEY'], algorithms=["HS256"])
        return payload 
    except: 
        return None

def verify_credentials(username: str, password: str):
    try:
        client = MongoClient('mongodb+srv://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' + os.environ['MONGODB_CLUSTERNAME'] + '.nsb6k.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
        database = client['Visser']
        collection = database['users']
        
        user_document = collection.find_one({"username": username})
        auth = bcrypt.checkpw(str.encode(password), str.encode(user_document['password']))
        return auth 
    except:
        return False