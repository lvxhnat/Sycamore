from fastapi import APIRouter, Depends
from utils.auth.verify_utils import hasaccess

from routers.endpoints import (
    twitter,
    assets,
    agriculture,
)

protected_endpoint = [Depends(hasaccess)]

api_router = APIRouter()
api_router.include_router(
    twitter.router,
    tags=["Twitter"],
    dependencies=protected_endpoint
)
api_router.include_router(
    assets.router,
    tags=["Asset"],
    dependencies=protected_endpoint
)
api_router.include_router(
    agriculture.router,
    tags=["Agriculture"],
    dependencies=protected_endpoint
)
