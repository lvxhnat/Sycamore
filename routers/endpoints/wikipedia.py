import logging
import pandas as pd


from fastapi import APIRouter, HTTPException, Query

from sycamore.basemodels import wikipedia, writetypes
from sycamore.scrapers.wikipedia import WikipediaScraperClient
from sycamore.utils.storage_utils import StorageUtility
from sycamore.utils.cleaning_utils import CleaningUtility

router = APIRouter(
    prefix="/wiki",
)


@router.get("/companypageviews")
def scrape_and_write_wikipedia_companypageviews_task():

    storage_util = StorageUtility()

    logging.info(
        "Twitter Followings Scraper: Twitter followings extraction completed")
