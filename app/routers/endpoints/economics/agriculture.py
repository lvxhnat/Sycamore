from doctest import DocFileCase, DocFileSuite
import os
import jwt
import time
from dotenv import load_dotenv
from typing import Optional

from fastapi import APIRouter, HTTPException, Header

from app.models.writetype import storage_type
from app.models.endpoints.agriculture import AgriculturalResponse
from app.scrapers.economics.agriculture.eia import EIAScraperClient
from app.scrapers.economics.agriculture.usda import USDAScraperClient
from app.utils.storage.cloud_utils import CloudUtility
from app.utils.storage.storage_urls import ethanol_prod_storage_url, ethanol_stock_storage_url

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
        ethanol_api_client = EIAScraperClient()
        df = ethanol_api_client.get_weekly_ethanol_production_levels()
        cloud_singleton = CloudUtility()
        cloud_singleton.write_to_cloud_storage(
            dataframe=df, storage_url=ethanol_prod_storage_url())

        return df

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
        ethanol_api_client = EIAScraperClient()
        df = ethanol_api_client.get_weekly_ethanol_ending_stocks()
        cloud_singleton = CloudUtility()
        cloud_singleton.write_to_cloud_storage(
            dataframe=df, storage_url=ethanol_stock_storage_url())

        return df

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
        usda_api_client = USDAScraperClient()
        crop_production_report_data = usda_api_client.get_crop_production_reports()
        return crop_production_report_data

    except Exception as e:
        return HTTPException(400, detail=e)
