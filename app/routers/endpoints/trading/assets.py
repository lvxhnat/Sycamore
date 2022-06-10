from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Header

from app.utils.storage.cloud_utils import CloudUtility
from app.scrapers.trading.main import TradingDataClient
from app.utils.storage.storage_urls import trading_metadata_storage_url
from app.models.endpoints.trading import HistoricalDataParams


load_dotenv()

router = APIRouter(
    prefix="/trading",
)

trading_client = TradingDataClient()


@router.post("/historical")
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
            json = {
                "ticker": "AAPL",
                "from_date": "2022-01-01",
                "to_date": "2022-02-02",
                "resolution": "15MIN",
                "instrument": "Stock",
                "write_type": "return"
            },
            headers = {
                "token": api_token
            }).json()
    ```
    """

    def get_formatted_historical_data(x):
        return trading_client.get_historical_data(
            ticker=params.ticker, from_date=params.from_date, to_date=params.to_date, resolution=params.resolution, data_format=x)

    try:
        df = get_formatted_historical_data("csv")
        print(df)
        cloud_singleton = CloudUtility()
        write_path = cloud_singleton.write_to_cloud_storage(
            dataframe=df, storage_url=trading_metadata_storage_url({
                "ticker": params.ticker,
                "from_date": params.from_date,
                "to_date": params.to_date,
                "resolution": params.resolution,
                "instrument": params.instrument,
            }))
        response = list(df.T.to_dict().values())
        return {
            "response": response,
            "write_path": write_path
        }

    except Exception as e:
        print(e)
        return HTTPException(400, detail=e)
