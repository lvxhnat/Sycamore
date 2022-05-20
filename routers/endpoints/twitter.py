import os
import jwt
import sys
import uuid
import time
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from models import twitter
from alerts.logger import logger
from utils.storage_utils import StorageUtility
from utils.cleaning_utils import CleaningUtility
from scrapers.social.twitter import TwitterScraperClient
from decorators.endpointdec import store_mongodb_metadata

from fastapi import APIRouter, HTTPException, Header

load_dotenv()
sys.path.append("...")


router = APIRouter(
    prefix="/twitter",
)
twitter_api_keys = 11  # Number of API Keys to deploy for twitter
def check_user_length(s): return 0 if s is None else len(s)


@router.post("/followings", response_model=twitter.FollowingsResponse)
@store_mongodb_metadata
def scrape_and_write_twitter_followings_task(
        params: twitter.FollowingsParams,
        token: str = Header(...),
):
    jwt_payload = jwt.decode(
        token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])
    neither_defined = (params.user_ids or params.screen_names) is None
    endpoint = "twitter_followings"

    if neither_defined:
        raise HTTPException(
            status_code=404,
            detail="Error 404: screen id or screen name needs to be defined",
        )

    start_time = time.time()

    twitter_api_client = TwitterScraperClient(api_keys=twitter_api_keys)

    twitter_followings_data = pd.concat(twitter_api_client.iter_processed_followings(
        screen_names=params.screen_names, user_ids=params.user_ids))

    cleaning_util = CleaningUtility()

    twitter_followings_data = cleaning_util.clean_twitter_follows(
        twitter_followings_data)
    users_extracted = twitter_followings_data.twitter_follower_id.nunique()
    users_requested = check_user_length(
        params.screen_names) + check_user_length(params.user_ids)

    storage_util = StorageUtility()
    storage_url = storage_util.store_items(
        twitter_followings_data,
        user=jwt_payload['user'],
        write_type=params.write_type,
        endpoint_storage=endpoint)

    time_elapsed = round(time.time() - start_time)

    extraction_metadata = {
        "user": jwt_payload['user'],
        "end_point": '/'.join(endpoint.split("_")),
        "date_extracted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "job_id": str(uuid.uuid4()),
        "write_type": params.write_type,
        "job_description": {
            "users_requested": users_requested,
            "users_requested_extracted": users_extracted,
        },
        "time_elapsed_seconds": time_elapsed,
        "write_path": storage_url,
    }

    return extraction_metadata


@router.post("/followers", response_model=twitter.FollowersResponse)
@store_mongodb_metadata
def scrape_and_write_twitter_followers_task(
        params: twitter.FollowersParams,
        token: str = Header(...),
):
    jwt_payload = jwt.decode(
        token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])
    neither_defined = (params.user_ids or params.screen_names) is None
    endpoint = "twitter_followers"

    if neither_defined:
        raise HTTPException(
            status_code=404,
            detail="Error 404: screen id or screen name needs to be defined"
        )

    start_time = time.time()

    twitter_api_client = TwitterScraperClient(api_keys=twitter_api_keys)

    twitter_followers_data = pd.concat(twitter_api_client.iter_processed_followers(
        screen_names=params.screen_names, user_ids=params.user_ids))

    cleaning_util = CleaningUtility()

    twitter_followers_data = cleaning_util.clean_twitter_follows(
        twitter_followers_data)
    users_extracted = twitter_followers_data.twitter_follower_id.nunique()
    users_requested = check_user_length(
        params.screen_names) + check_user_length(params.user_ids)

    storage_util = StorageUtility()
    storage_url = storage_util.store_items(
        twitter_followers_data,
        write_type=params.write_type,
        user=jwt_payload['user'],
        endpoint_storage=endpoint)

    time_elapsed = round(time.time() - start_time)

    extraction_metadata = {
        "user": jwt_payload['user'],
        "job_id": str(uuid.uuid4()),
        "end_point": '/'.join(endpoint.split("_")),
        "write_type": params.write_type,
        "job_description": {
            "users_requested": users_requested,
            "users_requested_extracted": users_extracted,
        },
        "time_elapsed_seconds": time_elapsed,
        "write_path": storage_url,
    }

    return extraction_metadata
