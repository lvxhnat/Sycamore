from fastapi import APIRouter, Depends

from app.routers.endpoints.social import twitter, streams
from app.routers.endpoints.economics import agriculture
from app.routers.endpoints.trading import assets

from app.utils.auth.auth_utils import hasaccess


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

# api_router.include_router(
#     streams.router,
#     tags=["Streams"],
#     dependencies=protected_endpoint
# )
