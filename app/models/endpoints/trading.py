from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional, List
from typing_extensions import Literal

from app.models.endpoints.base import DefaultBaseModel
from app.models.writetype import storage_type
load_dotenv()

SupportAssetTypes = Literal["Stock", "Forex", "Crypto"]
SupportedTradingResolutions = Literal["1MIN", "5MIN", "15MIN", "30MIN", "1H", "D", "5D", "15D",
                                      "30D", "60D", "W", "5W", "15W", "30W", "60W", "M", "5M", "15M", "30M", "60M"]


class AssetHistoricalData(BaseModel):
    # Data Returned directly from the scrapers
    close: float
    high: float
    open: float
    low: float
    date: int
    volume: int
    symbol: str


class DefaultTradingParamsBaseModel(BaseModel):
    ticker: str = Field(
        "NFLX", description="The ticker symbol given.")
    from_date: str = Field(
        "2021-01-01", description="Date we want to get our ticker data from. In format %Y-%m-%d")
    to_date: str = Field(
        datetime.today().strftime("%Y-%m-%d"), description="Date we want to get our ticker data to. In format %Y-%m-%d")
    resolution: str = Field(
        "1M", description="The resolution/interval of our data. ")
    instrument: str = Field(
        default="Stock", description="The financial instrument. Stock, Cryptocurrency, Futures, Options."
    )
    return_data: Optional[bool] = True


class DefaultTradingResponseBaseModel(DefaultBaseModel):

    class Config:
        schema_extra = {
            "example": {
                "user": "james201",
                "end_point": "historicaldata/AAPL/",
                "date_extracted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "job_id": '12c6f2a1-8022-4965-b5fe-e210b7e4deba',
                "write_type": 'mongodb',
                "job_description": {
                    "number_of_rows": 2000
                },
                "time_elapsed_seconds": 43411,
                "write_path": 'mongodb("Visser", "historical_data")'
            }
        }


class HistoricalDataListResponse(BaseModel):
    response: List[AssetHistoricalData]
    write_path: str


class HistoricalDataParams(DefaultTradingParamsBaseModel):
    pass


class HistoricalDataWriteResponse(DefaultTradingResponseBaseModel):
    pass
