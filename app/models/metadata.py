from pydantic import BaseModel
from datetime import datetime


class UserCallMetadataInterface(BaseModel):
    _id: str
    endpoint_called: str
    date_extracted: datetime
    user: str
    time_elapsed: int
    status: str


class HistoricalTradingMetadataInterface(BaseModel):
    _id: str
    ticker: str
    from_date: datetime
    to_date: datetime
    resolution: str
    instrument: str
    write_path: str
