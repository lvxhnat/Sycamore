import os
import jwt
import sys
import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta

from databases.mongodbclients import user_collection

sys.path.append("...")


load_dotenv()


def generate_token(username: str):
    def payload(x): return {
        "exp": datetime.timestamp(datetime.now() + timedelta(hours=x)),
        "user": username,
    }
    access_token = jwt.encode(payload(
        int(os.environ['ACCESS_KEY_LIFETIME'])), os.environ['MASTER_SECRET_KEY'])
    return access_token


def verify_token(jwt_token: str):
    try:
        payload = jwt.decode(
            jwt_token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])
        return payload
    except:
        return None


def verify_credentials(username: str, password: str):
    try:
        user_document = user_collection.find_one(
            {"username": username})
        auth = bcrypt.checkpw(str.encode(password),
                              str.encode(user_document['password']))
        return auth
    except:
        return False
