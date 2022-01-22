import os
import sys
import pandas as pd

sys.path.append("...")

from typing import Optional, Tuple
from fastapi import APIRouter, HTTPException, Query

from basemodels import twitter, writetypes
from scrapers.twitter import TwitterScraperClient
from utils.storage_utils import StorageUtility
from utils.cleaning_utils import CleaningUtility
from alerts.logger import logger


router = APIRouter(
    prefix="/twitter",
)
twitter_api_keys = 11  # Number of API Keys to deploy for twitter


@router.post("/followings")
def scrape_and_write_twitter_followings_task(
        params: twitter.FollowingsBaseModel,
        write_type: Optional[writetypes.StorageWriteType] = "localstorage") -> Tuple[pd.DataFrame, str]:

    neither_defined = (params.user_ids or params.screen_names) is None
    endpoint = "twitter_followings"

    if neither_defined:
        raise HTTPException(
            status_code=404,
            detail="One of screen id or screen name needs to be defined",
        )

    twitter_api_client = TwitterScraperClient(api_keys=twitter_api_keys)

    twitter_followings_data = pd.concat(twitter_api_client.iter_processed_followings(
        screen_names=params.screen_names, user_ids=params.user_ids))

    cleaning_util = CleaningUtility()

    twitter_followings_data = cleaning_util.clean_twitter_follows(
        twitter_followings_data)

    storage_util = StorageUtility()
    storage_url = storage_util.store_items(
        twitter_followings_data,
        write_type=write_type,
        endpoint_storage=endpoint)

    write_location = write_type.replace("storage", "")
    # cd .. and join the storage url
    storage_url = os.path.dirname(os.path.realpath(
        '__file__')) + "/" + storage_url.replace("..", "")
    logger.info(
        "Twitter Followings Scraper: Twitter followings extraction completed")

    return(twitter_followings_data, f"Data written to {write_location} storage under path: {storage_url}")


@router.post("/followers")
def scrape_and_write_twitter_followers_task(
        params: twitter.FollowersBaseModel,
        write_type: Optional[writetypes.StorageWriteType] = "localstorage") -> Tuple[pd.DataFrame, str]:

    neither_defined = (params.user_ids or params.screen_names) is None
    endpoint = "twitter_followers"

    if neither_defined:
        raise HTTPException(
            status_code=404,
            detail="One of screen id or screen name needs to be defined",
        )

    twitter_api_client = TwitterScraperClient(api_keys=twitter_api_keys)

    twitter_followers_data = pd.concat(twitter_api_client.iter_processed_followers(
        screen_names=params.screen_names, user_ids=params.user_ids))

    cleaning_util = CleaningUtility()

    twitter_followers_data = cleaning_util.clean_twitter_follows(
        twitter_followers_data)

    storage_util = StorageUtility()
    storage_url = storage_util.store_items(
        twitter_followers_data,
        write_type=write_type,
        endpoint_storage=endpoint)

    write_location = write_type.replace("storage", "")
    # cd .. and join the storage url
    storage_url = os.path.dirname(os.path.realpath(
        '__file__')) + "/" + storage_url.replace("..", "")
    logger.info(
        "Twitter Followers Scraper: Twitter followers extraction completed")

    return(twitter_followers_data, f"Data written to {write_location} storage under path: {storage_url}")
