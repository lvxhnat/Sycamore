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
from fastapi_utils.cbv import cbv

from models.writetype import storage_type
from models.decorators.mongodb import store_mongodb_metadata
from models.trading import HistoricalDataParams, HistoricalDataResponse


load_dotenv()

router = APIRouter(
    prefix="/trading",
)


@cbv(router)
class TradingCBV:

    write_type: Optional[storage_type] = "cloudstorage"
    token: str = Header(...)
    trading_client = TradingDataClient()

    @router.get("/historical", response_model=HistoricalDataResponse)
    @store_mongodb_metadata
    def scrape_and_write_historical_data(self, params: HistoricalDataParams):

        try:

            jwt_payload = jwt.decode(
                self.token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])
            start_time = time.time()
            historical_data = self.trading_client.get_historical_data(
                params.ticker,
                params.from_date,
                params.to_date,
                params.resolution,
                params.instruments)

            endpoint = f"historicaldata/{params.ticker}"

            storage_util = StorageUtility()
            storage_url = storage_util.store_items(
                historical_data,
                user=jwt_payload['user'],
                write_type=self.write_type,
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
                "write_type": self.write_type,
                "job_description": {
                    "number_of_rows": len(historical_data)
                },
                "time_elapsed_seconds": time_elapsed,
                "write_path": storage_url,
            }

            return extraction_metadata

        except Exception as e:
            return HTTPException(400, detail=e)
