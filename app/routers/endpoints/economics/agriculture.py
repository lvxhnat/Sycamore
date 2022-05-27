import os
import jwt
import time
from dotenv import load_dotenv
from typing import Optional

from fastapi import APIRouter, HTTPException, Header

from app.models.writetype import storage_type
from app.models.agriculture import AgriculturalResponse
from app.utils.alerts.metadata_logger import log_metadata
from app.scrapers.economics.agriculture.eia import EIAScraperClient
from app.scrapers.economics.agriculture.usda import USDAScraperClient
from app.utils.storage_utils import StorageUtility

load_dotenv()

router = APIRouter(
    prefix="/agriculture",
)


@router.get("/ethanolprod", response_model=AgriculturalResponse)
def scrape_and_write_weekly_ethanol_production(
        write_type: Optional[storage_type] = "cloudstorage",
        token: str = Header(...),
):
    '''
    Get the weekly ethanol production levels in continental united states
    '''

    try:
        jwt_payload = jwt.decode(
            token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])
        endpoint = "agriculture_ethanolprod"
        start_time = time.time()

        ethanol_api_client = EIAScraperClient()

        ethanol_data = ethanol_api_client.get_weekly_ethanol_production_levels()

        storage_util = StorageUtility()
        storage_url = storage_util.store_items(
            ethanol_data,
            user=jwt_payload['user'],
            write_type=write_type,
            endpoint_storage=endpoint)

        # cd .. and join the storage url
        storage_url = os.path.dirname(os.path.realpath(
            '__file__')) + "/" + storage_url.replace("..", "")

        return log_metadata(user=jwt_payload['user'],
                            endpoint='/'.join(endpoint.split("_")),
                            write_type=write_type,
                            job_description={},
                            time_elapsed_seconds=round(
                                time.time() - start_time),
                            write_path=storage_url)

    except Exception as e:
        return HTTPException(400, detail=e)


@router.get("/ethanolstock", response_model=AgriculturalResponse)
def scrape_and_write_weekly_ethanol_ending_stocks(
    write_type: Optional[storage_type] = "cloudstorage",
    token: str = Header(...),
):
    '''
    Get the weekly ethanol production levels in continental united states
    '''

    try:
        jwt_payload = jwt.decode(
            token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])
        endpoint = "agriculture_ethanolstock"
        start_time = time.time()

        ethanol_api_client = EIAScraperClient()

        ethanol_data = ethanol_api_client.get_weekly_ethanol_ending_stocks()

        storage_util = StorageUtility()
        storage_url = storage_util.store_items(
            ethanol_data,
            user=jwt_payload['user'],
            write_type=write_type,
            endpoint_storage=endpoint)

        # cd .. and join the storage url
        storage_url = os.path.dirname(os.path.realpath(
            '__file__')) + "/" + storage_url.replace("..", "")

        return log_metadata(user=jwt_payload['user'],
                            endpoint='/'.join(endpoint.split("_")),
                            write_type=write_type,
                            job_description={},
                            time_elapsed_seconds=round(
                                time.time() - start_time),
                            write_path=storage_url)

    except Exception as e:
        return HTTPException(400, detail=e)


@router.get("/cropreports", response_model=AgriculturalResponse)
def scrape_and_write_usda_crop_production_reports(
    write_type: Optional[storage_type] = "cloudstorage",
    token: str = Header(...),
):
    '''
    Get the weekly ethanol production levels in continental united states
    '''

    try:
        jwt_payload = jwt.decode(
            token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])
        endpoint = "agriculture_cropreports"
        start_time = time.time()

        usda_api_client = USDAScraperClient()

        crop_production_report_data = usda_api_client.get_crop_production_reports()

        storage_util = StorageUtility()
        storage_url = storage_util.store_items(
            crop_production_report_data,
            user=jwt_payload['user'],
            write_type=write_type,
            endpoint_storage=endpoint)

        # cd .. and join the storage url
        storage_url = os.path.dirname(os.path.realpath(
            '__file__')) + "/" + storage_url.replace("..", "")

        return log_metadata(user=jwt_payload['user'],
                            endpoint='/'.join(endpoint.split("_")),
                            write_type=write_type,
                            job_description={},
                            time_elapsed_seconds=round(
                                time.time() - start_time),
                            write_path=storage_url)

    except Exception as e:
        return HTTPException(400, detail=e)
