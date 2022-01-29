from alerts.logger import logger
from utils.cleaning_utils import CleaningUtility
from utils.storage_utils import StorageUtility
from scrapers.assets import AssetScraperClient
from models import asset
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Tuple
import os
import sys
import pandas as pd

sys.path.append("...")


router = APIRouter(
    prefix="/assets",
)
