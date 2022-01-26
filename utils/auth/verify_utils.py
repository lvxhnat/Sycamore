import os
import jwt
from dotenv import load_dotenv
load_dotenv()
from fastapi import HTTPException, Header

async def hasaccess(token: str = Header(...)):
    """
        Function that is used to validate the token in the case that it requires it
    """

    try:

        jwt.decode(token, key = os.environ['MASTER_SECRET_KEY'], algorithms = ["HS256"])
        
    except: 

        raise HTTPException(status_code = 401, detail = "Token is invalid. Please request new token or try again")