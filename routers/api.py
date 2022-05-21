from fastapi import APIRouter, Depends

from routers.endpoints.social import twitter
from routers.endpoints.economics import agriculture
from routers.endpoints.trading import assets

from utils.auth.auth_utils import hasaccess


protected_endpoint = [Depends(hasaccess)]

api_router = APIRouter()
api_router.include_router(
    twitter.router,
    tags=["Twitter"],
    dependencies=protected_endpoint
)

api_router.include_router(
    agriculture.router,
    tags=["Agriculture"],
    dependencies=protected_endpoint
)

api_router.include_router(
    assets.router,
    tags=["Asset"],
    dependencies=protected_endpoint
)
