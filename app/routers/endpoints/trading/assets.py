import os
import jwt
import time
from dotenv import load_dotenv
from typing import Union, List
from fastapi import APIRouter, HTTPException, Header

from app.scrapers.trading.main import TradingDataClient
from app.utils.storage_utils import StorageUtility
from app.utils.alerts.logger import logging
from app.caching.main_layers import record_trading_metadata
from app.models.trading import AssetHistoricalData, HistoricalDataParams, HistoricalDataWriteResponse

load_dotenv()

router = APIRouter(
    prefix="/trading",
)

trading_client = TradingDataClient()


@router.post("/historical", response_model = Union[HistoricalDataWriteResponse, List[AssetHistoricalData]])
def get_historical_data(params: HistoricalDataParams,
                        token: str = Header(...),):
    """
    ### Parameters 
    -------------
    **ticker**     : The ticker symbol <br/>
    **from_date**  : Start date we want to get our data from, in format %Y-%m-%d <br/>
    **to_date**    : End date we want to get our data from, in format %Y-%m-%d <br/>
    **resolution** : Supported resolutions are - <br/>
            &emsp;&emsp; MINUTE: 1MIN, 5MIN, 15MIN, 30MIN, <br/>
            &emsp;&emsp; HOUR: 1H <br/>
            &emsp;&emsp; DAY: 1D, 5D, 15D, 30D, 60D <br/>
            &emsp;&emsp; WEEK: 1W, 5W, 15W, 30W, 60W <br/>
            &emsp;&emsp; MONTH: 1M, 5M, 15M, 30M, 60M <br/>

    ### Example Python Request
    -------------
    ```python
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
    ```
    """
    endpoint = "/historical"

    def get_formatted_historical_data(x): return trading_client.get_historical_data(
        ticker=params.ticker, from_date=params.from_date, to_date=params.to_date, resolution=params.resolution, data_format=x)

    try:
        jwt_payload = jwt.decode(
            token, os.environ['MASTER_SECRET_KEY'], algorithms=["HS256"])

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

        meta_data = record_trading_metadata(user=jwt_payload['user'],
                                            endpoint='/'.join(endpoint.split("_")),
                                            write_type=params.write_type,
                                            job_metadata={
            "number_of_rows": len(historical_data)},
            time_elapsed_seconds=round(
            time.time() - start_time),
            write_path=storage_url)

        return historical_data if is_return_type else meta_data

    except Exception as e:
        logging.error(e)
        return HTTPException(400, detail=e)
