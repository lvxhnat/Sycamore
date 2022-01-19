import os
import pandas as pd

from typing import Optional, Tuple
from fastapi import APIRouter, HTTPException, Query

from sycamore.basemodels import asset, writetypes
from sycamore.scrapers.assets import AssetScraperClient
from sycamore.utils.storage_utils import StorageUtility
from sycamore.utils.cleaning_utils import CleaningUtility
from sycamore.alerts.logger import logger


router = APIRouter(
    prefix="/assets",
)
