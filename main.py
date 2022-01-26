from http.client import HTTPException
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from utils.auth import auth_utils
from routers import api

from starlette.requests import Request

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Sycamore",
    description="Sycamore is a scraper designed for use within the heron project environment, tailored for financial related data endpoints",
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

@app.post("/requestauthtoken")
@limiter.limit("5/minute")
async def request_auth_token(request: Request):
    try:
        params = await request.form()
        _user = params['username']
        _pass = params['password']
        print(_user, _pass)
        authenticated = auth_utils.verify_credentials(_user, _pass)
        if authenticated: 
            access_token = auth_utils.generate_token(_user)
            return { "access_token" : access_token }
        else: 
            raise HTTPException(status_code = 401, detail = "Invalid Username or Password Supplied")    
    except:
        raise HTTPException(status_code = 401, detail = "Invalid Payload Headers Supplied. Make sure payload contains username and password fields")

app.include_router(api.api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1236)