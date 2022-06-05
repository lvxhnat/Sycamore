import pandas as pd
from dotenv import load_dotenv

from app.models.endpoints import social
from app.utils.cleaning.platform.twitter_clean import clean_twitter_follows
from app.scrapers.social.twitter import TwitterScraperClient

from fastapi import APIRouter, HTTPException, Header

from app.utils.storage.cloud_utils import CloudUtility
from app.utils.storage.storage_urls import twitter_followers_storage_url, twitter_followings_storage_url

load_dotenv()

router = APIRouter(
    prefix="/twitter",
)
twitter_api_keys = 11  # Number of API Keys to deploy for twitter
def check_user_length(s): return 0 if s is None else len(s)


@router.post("/followings", response_model=social.FollowingsResponse)
def scrape_and_write_twitter_followings_task(
        params: social.FollowingsParams,
        token: str = Header(...),
):
    """
    # Parameters
    -------------
    **user_ids**        : List of user id strings or integers in format: [...] or [..., ..., ...]
    **screen_names**    : List of user id strings or integers in format: [...] or [..., ..., ...]
    **return_data**     : Optional[bool], Defaults as True

    # Example Python Request
    -------------
    ```python
    >>> requests.post(f"http://localhost:8080/api/twitter/followings",
            data = json.dumps({
                "user_ids": [],
                "screen_names": ["donaldtrump", "koolaid"]
                "return_data": "true"
            }),
            headers = {
                "token": api_token
            }).json()
    ```
    """
    if (params.user_ids or params.screen_names) is None:
        raise HTTPException(
            status_code=404,
            detail="Error 404: screen id or screen name needs to be defined",
        )

    twitter_api_client = TwitterScraperClient(api_keys=twitter_api_keys)

    df = clean_twitter_follows(pd.concat(twitter_api_client.iter_processed_followings(
        screen_names=params.screen_names, user_ids=params.user_ids)))

    cloud_singleton = CloudUtility()
    cloud_singleton.write_to_cloud_storage(
        dataframe=df, storage_url=twitter_followings_storage_url(params))

    return df


@router.post("/followers", response_model=social.FollowersResponse)
def scrape_and_write_twitter_followers_task(
        params: social.FollowersParams,
        token: str = Header(...),):
    """
    # Parameters
    -------------
    **user_ids**        : List of user id strings or integers in format: [...] or [..., ..., ...]
    **screen_names**    : List of user id strings or integers in format: [...] or [..., ..., ...]
    **return_data**     : Optional[bool], Defaults as True

    # Example Python Request
    -------------
    ```python
    >>> requests.post(f"http://localhost:8080/api/twitter/followers",
            data = json.dumps({
                "user_ids": [],
                "screen_names": ["donaldtrump", "koolaid"]
                "return_data": "true"
            }),
            headers = {
                "token": api_token
            }).json()
    ```
    """

    if (params.user_ids or params.screen_names) is None:
        raise HTTPException(
            status_code=404,
            detail="Error 404: screen id or screen name needs to be defined"
        )

    twitter_api_client = TwitterScraperClient(api_keys=twitter_api_keys)

    df = clean_twitter_follows(pd.concat(twitter_api_client.iter_processed_followers(
        screen_names=params.screen_names, user_ids=params.user_ids)))

    cloud_singleton = CloudUtility()
    cloud_singleton.write_to_cloud_storage(
        dataframe=df, storage_url=twitter_followers_storage_url(len(params.user_ids)))

    return df
