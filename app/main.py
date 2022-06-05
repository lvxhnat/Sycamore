import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler


import os
import jwt
import uuid
import time
import fastapi
import pandas as pd
from datetime import datetime

from app.routers import api
from app.utils.auth import auth_utils
from app.utils.alerts.logger import logging
from app.models.metadata import UserCallMetadataInterface
from app.middleware.entrypoint import plugin_metadata_producer
from app.models.singletons.mongodbclients import user_call_metadata_collection

limiter = Limiter(key_func=get_remote_address)
description = """ 
Visser is a data extraction application for data needs, allowing you to see the world in context 🌎 \n 
Visser scrapes and cleans data via Scrapers (Scrapy, Requests) and API calls asynchronously. A choice is then given to either store data in Google Cloud (GCS), MongoDB or Locally (If you do decide to pull down the codebase and run locally). 
\n\n 
Please contact me for an auth token if you wish to share the data available here!
"""
app = FastAPI(
    title="Visser",
    description=description,
    version="0.0.8",
    root_apth="/",
    contact={
        "name": "Yi Kuang",
        "email": "yikuang5@gmail.com"
    }
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


async def set_body(request: fastapi.Request):
    receive_ = await request._receive()

    async def receive():
        return receive_

    request._receive = receive


@app.middleware("http")
async def add_process_time_header(request: fastapi.Request, call_next):

    endpoint = request.scope['path']

    if endpoint in plugin_metadata_producer.keys():  # Available endpoints

        await set_body(request)

        params = await request.json()

        start_time = time.time()

        FUNC_RESULTS: pd.DataFrame = await call_next(request)

        time_elapsed = round(time.time() - start_time)
        token = request.headers['token']

        user_call_metadata: UserCallMetadataInterface = {
            "_id": str(uuid.uuid4()),
            "endpoint_called": endpoint,
            "date_extracted": datetime.today(),
            "user": jwt.decode(token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"]),
            "time_elapsed": time_elapsed,
            "status": FUNC_RESULTS.status_code if isinstance(FUNC_RESULTS, HTTPException) else 200,
        }
        log_metadata_plugin = plugin_metadata_producer[endpoint](params)

        if not log_metadata_plugin:
            raise HTTPException(
                status_code=422, detail=f"Failed to write {endpoint} metadata due to KeyError for endpoint")

        else:
            user_call_metadata_collection.insert_one(user_call_metadata)
            return FUNC_RESULTS

    else:
        return await call_next(request)

origins = [
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
def home_page():
    response = RedirectResponse(url="/docs")
    return response


@app.post("/token", tags=["Authentication"],)
@limiter.limit("10/minute")
async def request_auth_token(request: fastapi.Request):
    """
    ### Example Python Request
    -------------
    ```python
    >>> requests.post("http://localhost:8080/requestauthtoken", data = {
        "username": "username", 
        "password": "password"
    })
    ```
    """
    try:
        params = await request.form()
        _user = params['username']
        _pass = params['password']
        logging.info(
            "Verifying from mongoDB... ....")
        authenticated = auth_utils.verify_credentials(_user, _pass)
        logging.info(
            f"""User is {"authenticated" if authenticated else "not authenticated!"}""")
        if authenticated:
            access_token = auth_utils.generate_token(_user)
            return {"access_token": access_token, "token_type": "bearer"}

        else:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"})

    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail="Invalid Payload Headers Supplied. Make sure payload contains username and password fields",
            headers={"WWW-Authenticate": "Bearer"})

app.include_router(api.api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1236, reload=True)
