from http.client import HTTPException
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from params.auth import AuthParams
from utils.auth import auth_utils
from routers import api

app = FastAPI(
    title="Sycamore",
    description="Sycamore is a scraper designed for use within the heron project environment, tailored for financial related data endpoints",
)

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
def login(params: AuthParams):
    try:
        print(params.username, params.password)
        authenticated = auth_utils.verify_credentials(params.username, params.password)
        if authenticated: 
            access_token = auth_utils.generate_token(params.username)
            return { "access_token" : access_token }
        else: 
            raise HTTPException(status_code = 401, detail = "Invalid Username or Password Supplied")    
    except Exception as e:
        print(e)
        raise HTTPException(status_code = 401, detail = "Invalid Payload Headers Supplied. Make sure payload contains username and password fields")

app.include_router(api.api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1236)