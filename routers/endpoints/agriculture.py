import os
import sys 
import pandas as pd

sys.path.append("...")

from typing import Optional, Tuple
from fastapi import APIRouter, HTTPException, Query

from scrapers.eia import EIAScraperClient
from scrapers.usda import USDAScraperClient

from params.output.agriculture import AgriculturalOutput
from basemodels import agriculture, writetypes
from utils.storage_utils import StorageUtility
from alerts.logger import logger

router = APIRouter(
    prefix="/agriculture",
)


@router.get("/ethanolprod", response_model=AgriculturalOutput)
def scrape_and_write_weekly_ethanol_production(
        params: agriculture.DefaultAgriculturalBaseModel,
        write_type: Optional[writetypes.StorageWriteType] = "localstorage") -> Tuple[pd.DataFrame, str]:
    '''
    Get the weekly ethanol production levels in continental united states
    '''
    endpoint = "ethanol_prod"

    ethanol_api_client = EIAScraperClient()

    ethanol_data = asset_api_client.get_weekly_ethanol_production_levels()

    storage_util = StorageUtility()
    storage_url = storage_util.store_items(
        ethanol_data,
        write_type=write_type,
        endpoint_storage=endpoint)

    write_location = write_type.replace("storage", "")
    # cd .. and join the storage url
    storage_url = os.path.dirname(os.path.realpath(
        '__file__')) + "/" + storage_url.replace("..", "")
    logger.info(
        "Agriculture Ethanol Production Scraper: Ethanol production data extraction completed")

    return(ethanol_data, f"Data written to {write_location} storage under path: {storage_url}")


@router.get("/ethanolstock", response_model=AgriculturalOutput)
def scrape_and_write_weekly_ethanol_ending_stocks(
        params: agriculture.DefaultAgriculturalBaseModel,
        write_type: Optional[writetypes.StorageWriteType] = "localstorage") -> Tuple[pd.DataFrame, str]:
    '''
    Get the weekly ethanol production levels in continental united states
    '''
    endpoint = "ethanol_stock"

    ethanol_api_client = EIAScraperClient()

    ethanol_data = asset_api_client.get_weekly_ethanol_ending_stocks()

    storage_util = StorageUtility()
    storage_url = storage_util.store_items(
        ethanol_data,
        write_type=write_type,
        endpoint_storage=endpoint)

    write_location = write_type.replace("storage", "")
    # cd .. and join the storage url
    storage_url = os.path.dirname(os.path.realpath(
        '__file__')) + "/" + storage_url.replace("..", "")
    logger.info(
        "Agriculture Ethanol Ending Stock Scraper: Ethanol ending stock data extraction completed")

    return(ethanol_data, f"Data written to {write_location} storage under path: {storage_url}")


@router.get("/cropreports", response_model=AgriculturalOutput)
def scrape_and_write_usda_crop_production_reports(
        params: agriculture.DefaultAgriculturalBaseModel,
        write_type: Optional[writetypes.StorageWriteType] = "localstorage") -> Tuple[pd.DataFrame, str]:
    '''
    Get the weekly ethanol production levels in continental united states
    '''
    endpoint = "crop_production_reports"

    usda_api_client = USDAScraperClient()

    crop_production_report_data = usda_api_client.get_crop_production_reports()

    storage_util = StorageUtility()
    storage_url = storage_util.store_items(
        crop_production_report_data,
        write_type=write_type,
        endpoint_storage=endpoint)

    write_location = write_type.replace("storage", "")
    # cd .. and join the storage url
    storage_url = os.path.dirname(os.path.realpath(
        '__file__')) + "/" + storage_url.replace("..", "")
    logger.info(
        "Agriculture Crop Production Reports Scraper: Crop production report urls extraction completed")

    return(crop_production_report_data, f"Data written to {write_location} storage under path: {storage_url}")
