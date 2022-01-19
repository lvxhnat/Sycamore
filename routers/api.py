from fastapi import APIRouter, Depends

from routers.endpoints import (
    twitter,
    assets,
    agriculture,
)

api_router = APIRouter()
api_router.include_router(
    twitter.router,
    tags=["Twitter"],
)
api_router.include_router(
    assets.router,
    tags=["Asset"],
)
api_router.include_router(
    agriculture.router,
    tags=["Agriculture"],

)
