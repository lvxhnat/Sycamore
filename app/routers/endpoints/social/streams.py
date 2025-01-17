from app.utils.alerts.logger import logging
from app.scrapers.selenium.m3u8_scraper import retrieve_m3u8_url

from fastapi import APIRouter, HTTPException, Header

router = APIRouter(
    prefix="/streams",
)


@router.get("/watchlivestream", deprecated=True)
def get_livestream_url(
        token: str = Header(...),
):
    try:
        url = retrieve_m3u8_url()
        logging.info("Running!")
        return {"url": url}

    except Exception as e:
        logging.error(str(e))
        return HTTPException(400, detail=e)
