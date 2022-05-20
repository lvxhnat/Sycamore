import requests
import pandas as pd
from datetime import datetime, timedelta

from utils.alerts.logger import logger
from scrapers.base import BaseClient
from utils.cleaning.datetime_clean import date_to_unixtime


class FinnhubClient(BaseClient):

    """ Finnhub API data forms the base of this client
    """

    def __init__(self):
        super().__init__()

    def retrieve_symbols(
            self) -> pd.DataFrame:
        """ Get all the available Forex and Stock Symbols available on FinnHub API
        """

        try:
            forexSymbols = requests.get(
                f"https://finnhub.io/api/v1/forex/symbol?exchange=oanda&token={self.FINNHUB_APIKEY}").text
            stockSymbols = requests.get(
                f"https://finnhub.io/api/v1/stock/symbol?exchange=US&token={self.FINNHUB_APIKEY}").text

            supportStocks = pd.DataFrame(eval(stockSymbols))
            supportForex = pd.DataFrame(eval(forexSymbols))

            supportForex['type'] = "Forex"
            supportStocks = supportStocks.rename(
                columns={"currency": "Currency", "figi": "FIGI", "mic": "MIC"})
            symbols = pd.concat([supportStocks, supportForex])

            return symbols
        except:
            logger.error(
                f"Error occurred while retrieving symbols, please check request methods for finnhub api.")
            return None

    def get_historical_data(
        self,
        ticker: str,
        from_date: str = "2022-02-20",
        resolution: int = 1,
        data_format: str = "json"
    ) -> pd.DataFrame:
        """
        Parameters
        =============
        ticker -> [str]         : ticker name string
        from_date -> [str]      : %Y-%m-%d
        resolution -> [str]     : Supported resolution includes 1, 5, 15, 30, 60, D, W, M .Some timeframes might not be available depending on the exchange.
        data_format -> [str]    : the default data format to return, either json or csv

        Rate Limits
        =============
        60 API calls/minute
        """

        to_date = datetime.strftime(
            datetime.now() + timedelta(days=1), "%Y-%m-%d")
        fromdate, todate = date_to_unixtime(
            from_date, "%Y-%m-%d"), date_to_unixtime(to_date, "%Y-%m-%d")

        hist = requests.get(
            f"https://finnhub.io/api/v1/stock/candle?symbol={ticker}&resolution={resolution}&from={fromdate}&to={todate}&token={self.FINHUB_APIKEY}").text
        if data_format == "json":
            return hist

        elif data_format == "csv":
            historical = pd.DataFrame(eval(hist))
            historical.columns = ['close', 'high', 'low',
                                  'open', 'status', 'date', 'volume']
            historical.date = historical.date.apply(
                lambda ts: datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))

            historical['symbol'] = ticker
            return historical
