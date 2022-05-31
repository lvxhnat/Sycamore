from pydantic import BaseModel
from typing import Dict, Literal

from app.models.base import AllowedWriteTypes
from app.models.trading import SupportAssetTypes, SupportedTradingResolutions

class HistoricalDataModel(BaseModel):
    user: str
    job_id: str
    end_point: str
    write_type: AllowedWriteTypes
    write_path: str
    date_extracted: str
    job_description: Dict[str, str]
    time_elapsed_seconds: int
    ticker: str
    from_date: str
    to_date: str
    resolution: SupportedTradingResolutions
    instruments: SupportAssetTypes