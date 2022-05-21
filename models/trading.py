from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional

from models.base import DefaultBaseModel
from models.writetype import storage_type
load_dotenv()


class DefaultTradingParamsBaseModel(BaseModel):
    ticker: str = Field(None, description="The ticker symbol given.")
    from_date: str = Field(
        None, description="Date we want to get our ticker data from. In format %Y-%m-%d")
    to_date: str = Field(
        None, description="Date we want to get our ticker data to. In format %Y-%m-%d")
    resolution: str = Field(
        None, description="The resolution/interval of our data. ")
    instruments: str = Field(
        None, description="The financial instrument. Stock, Cryptocurrency, Futures, Options."
    )
    write_type: Optional[storage_type] = "return"

    class Config:
        schema_extra = {

        }


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


class HistoricalDataParams(DefaultTradingParamsBaseModel):
    pass


class HistoricalDataResponse(DefaultTradingResponseBaseModel):
    pass
