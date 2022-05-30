import os
import jwt
from jwt import InvalidTokenError
import bcrypt
from dotenv import load_dotenv
from datetime import datetime, timedelta

from fastapi import Header
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends

from app.models.singletons.mongodbclients import user_collection
from app.utils.alerts.exceptions.api_exception import credentials_exception

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def generate_token(username: str):
    def payload(x): return {
        "exp": datetime.timestamp(datetime.now() + timedelta(hours=x)),
        "user": username,
    }
    access_token = jwt.encode(payload(
        int(os.environ['ACCESS_KEY_LIFETIME'])), os.environ['MASTER_SECRET_KEY'])
    return access_token


def verify_token(jwt_token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            jwt_token,
            os.environ['MASTER_SECRET_KEY'],
            algorithms=["HS256"])
        user = payload['user']
        if user is None:
            raise credentials_exception()
        else:
            return user
    except InvalidTokenError:
        raise credentials_exception()


def verify_credentials(username: str, password: str):
    try:
        user_document = user_collection.find_one(
            {"username": username})
        auth = bcrypt.checkpw(str.encode(password),
                              str.encode(user_document['password']))
        return auth
    except:
        return False


async def hasaccess(token: str = Header(...)):
    """ Function that is used to validate the token in the case that it requires it
    """
    try:
        jwt.decode(
            token, key=os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])
    except:
        raise credentials_exception()
