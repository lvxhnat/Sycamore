from http.client import HTTPException
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.utils.auth import auth_utils
from app.routers import api

from starlette.requests import Request

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

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
    version="0.0.1",
    contact={
        "name": "Yi Kuang",
        "email": "yikuang5@gmail.com"
    }
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
@limiter.limit("5/minute")
async def request_auth_token(request: Request):
    """
    Example
    ==========
    requests.post("http://localhost:8080/requestauthtoken", data = {
        "username": "username", 
        "password": "password"
    })
    """
    try:
        params = await request.form()
        _user = params['username']
        _pass = params['password']
        authenticated = auth_utils.verify_credentials(_user, _pass)

        if authenticated:
            access_token = auth_utils.generate_token(_user)
            return {"access_token": access_token, "token_type": "bearere"}

        else:
            raise HTTPException(
                status_code=401,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"})

    except:
        raise HTTPException(
            status_code=404,
            detail="Invalid Payload Headers Supplied. Make sure payload contains username and password fields",
            headers={"WWW-Authenticate": "Bearer"})

app.include_router(api.api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1236)
