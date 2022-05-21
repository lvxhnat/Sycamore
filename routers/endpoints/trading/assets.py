import os
import jwt
import uuid
import time
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional

from scrapers.trading.main import TradingDataClient
from utils.storage_utils import StorageUtility

from fastapi import APIRouter, HTTPException, Header

from utils.auth.auth_utils import verify_credentials
from models.decorators.mongodb import store_mongodb_metadata
from models.trading import HistoricalDataParams, HistoricalDataResponse


load_dotenv()

router = APIRouter(
    prefix="/trading",
)

trading_client = TradingDataClient()


# @store_mongodb_metadata
@router.post("/historical", response_model=HistoricalDataResponse)
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
                  "resolution": "1D",
                  "instrument": "Stock",
              }),
             headers = { "token": api_token }).json()
    """
    try:
        jwt_payload = jwt.decode(
            token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])
        start_time = time.time()
        historical_data = trading_client.get_historical_data(
            params.ticker,
            params.from_date,
            params.to_date,
            params.resolution,
            params.instruments)

        if params.write_type == "return":
            serialized = historical_data.T.to_json()
            return serialized

        else:
            endpoint = f"historicaldata/{params.ticker}"
            storage_util = StorageUtility()
            storage_url = storage_util.store_items(
                historical_data,
                user=jwt_payload['user'],
                write_type=params.write_type,
                endpoint_storage=endpoint)

            # cd .. and join the storage url
            storage_url = os.path.dirname(os.path.realpath(
                '__file__')) + "/" + storage_url.replace("..", "")

            time_elapsed = round(time.time() - start_time)
            extraction_metadata = {
                "user": jwt_payload['user'],
                "end_point": '/'.join(endpoint.split("_")),
                "date_extracted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "job_id": str(uuid.uuid4()),
                "write_type": params.write_type,
                "job_description": {
                    "number_of_rows": len(historical_data)
                },
                "time_elapsed_seconds": time_elapsed,
                "write_path": storage_url,
            }

            return extraction_metadata

    except Exception as e:
        return HTTPException(400, detail=e)
