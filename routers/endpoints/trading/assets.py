import os
import jwt
import uuid
import time
from datetime import datetime
from dotenv import load_dotenv
from typing import Union, List

from scrapers.trading.main import TradingDataClient
from utils.storage_utils import StorageUtility
from utils.alerts.logger import logging

from fastapi import APIRouter, HTTPException, Header

from models.trading import AssetHistoricalData, HistoricalDataParams, HistoricalDataWriteResponse

load_dotenv()

router = APIRouter(
    prefix="/trading",
)

trading_client = TradingDataClient()


@router.post("/historical", response_model=Union[HistoricalDataWriteResponse, List[AssetHistoricalData]])
def get_historical_data(params: HistoricalDataParams,
                        token: str = Header(...),):
    """
    Example
    ==========
    >>> requests.post(f"http://localhost:8080/api/trading/historical", 
            data = json.dumps({
                "ticker": "AAPL",
                "from_date": "2022-01-01",
                "to_date": "2022-02-02",
                "resolution": "15MIN",
                "instrument": "Stock",
                "write_type": "return"
            }),
            headers = {
                "token": api_token
            }).json()
    """
    def get_formatted_historical_data(x): return trading_client.get_historical_data(
        ticker=params.ticker, from_date=params.from_date, to_date=params.to_date, resolution=params.resolution, data_format=x)

    try:
        jwt_payload = jwt.decode(
            token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])

        endpoint = f"historicaldata/{params.ticker}"
        start_time = time.time()
        storage_url = None
        is_return_type = params.write_type == "return"

        if is_return_type:
            historical_data = get_formatted_historical_data("json")

        else:
            historical_data = get_formatted_historical_data("csv")
            storage_util = StorageUtility()
            storage_url = storage_util.store_items(
                historical_data,
                user=jwt_payload['user'],
                write_type=params.write_type,
                endpoint_storage=endpoint)
            # cd .. and join the storage url
            storage_url = os.path.dirname(os.path.realpath(
                '__file__')) + "/" + storage_url.replace("..", "")

        meta_data = log_metadata(user=jwt_payload['user'],
                                 endpoint='/'.join(endpoint.split("_")),
                                 write_type=params.write_type,
                                 job_description={
                                     "number_of_rows": len(historical_data)},
                                 time_elapsed_seconds=round(
                                     time.time() - start_time),
                                 write_path=storage_url)

        return historical_data if is_return_type else meta_data

    except Exception as e:
        logging.error(e)
        return HTTPException(400, detail=e)
