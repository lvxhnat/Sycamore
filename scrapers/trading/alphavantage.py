import os
import csv
import requests
import numpy as np
import pandas as pd

from itertools import cycle
from dotenv import load_dotenv
from datetime import datetime

from utils.exceptions.api_exception import RateLimitException
env_loaded = load_dotenv()


class AlphaVantageClient:

    def __init__(self, keys_to_use: int = 16):
        ''' Keys has a rate limit of 500 per day'''
        self.APIKEYS = cycle(
            [os.environ['ALPHA_VANTAGE_API_KEY_' + str(key)] for key in range(keys_to_use)])
        self.APIKEY = next(self.APIKEYS)

    def get_historical_data(
            self,
            ticker: str,
            resolution: str = "5min",
            from_date: str = "2022-02-20",
            retries: int = 3) -> pd.DataFrame:
        """ Retrieve historical data from alpha vantage up to the last two years.

        ## Parameters
        ======================
        ticker      : Ticker symbol.
        resolution  : Data interval 1min, 5min, 15min, 30min, 60min
        date_range  : Date in %Y-%m-%d

        ## Sample Call 
        ======================
        >>> get_historical_data(ticker = "IBM")

        ## Results
        ======================
            time	            open	        high	        low	            close	        volume
        0	2021-11-08 20:00:00	121.381548423	121.381548423	121.381548423	121.381548423	130
        1	2021-11-08 19:59:00	121.381645887	121.381645887	121.381645887	121.381645887	150
        2	2021-11-08 19:45:00	121.381645887	121.381645887	121.381645887	121.381645887	553
        3	2021-11-08 19:31:00	121.342660293	121.342660293	121.342660293	121.342660293	259
        4	2021-11-08 19:21:00	121.381645887	121.381645887	121.381645887	121.381645887	100

        """

        def get_date_range(from_date: str):
            days = max(13 * 28, (datetime.today() -
                       datetime.strptime(from_date, "%Y-%m-%d")).days)
            months = np.ceil(days / 28).astype(int)
            return "year" + str(months//12) + "month" + str(months % 12)

        resolution = resolution.strip(" ").lower()

        try:
            date_range = get_date_range(from_date)

            base_endpoint = "https://www.alphavantage.co/query?"
            endpoint = f"function=TIME_SERIES_INTRADAY_EXTENDED\
                            &symbol={ticker}\
                            &interval={resolution}\
                            &slice={date_range}\
                            &apikey={self.APIKEY}"

            url = base_endpoint + endpoint

            with requests.Session() as s:
                download = s.get(url)
                decoded_content = download.content.decode('utf-8')
                cr = csv.reader(decoded_content.splitlines(), delimiter=',')
                my_list = list(cr)

            df = pd.DataFrame(my_list[1:], columns=my_list[0])

            assert df.shape[0] > 0

            return df

        except Exception:

            self.APIKEY = next(self.APIKEYS)

            if retries == 0:
                raise RateLimitException

            else:
                self.get_historical_data(
                    ticker=ticker,
                    resolution=resolution,
                    date_range=date_range,
                    retries=retries - 1)
