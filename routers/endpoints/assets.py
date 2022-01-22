import os
import sys
import pandas as pd

sys.path.append("...")

from typing import Optional, Tuple
from fastapi import APIRouter, HTTPException, Query

from basemodels import asset, writetypes
from scrapers.assets import AssetScraperClient
from utils.storage_utils import StorageUtility
from utils.cleaning_utils import CleaningUtility
from alerts.logger import logger


router = APIRouter(
    prefix="/assets",
)
