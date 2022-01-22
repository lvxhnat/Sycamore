import sys
import logging
import pandas as pd

sys.path.append("...")

from fastapi import APIRouter, HTTPException, Query

from basemodels import wikipedia, writetypes
from scrapers.wikipedia import WikipediaScraperClient
from utils.storage_utils import StorageUtility
from utils.cleaning_utils import CleaningUtility

router = APIRouter(
    prefix="/wiki",
)


@router.get("/companypageviews")
def scrape_and_write_wikipedia_companypageviews_task():

    storage_util = StorageUtility()

    logging.info(
        "Twitter Followings Scraper: Twitter followings extraction completed")
