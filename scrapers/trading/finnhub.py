import time
import requests
import pandas as pd
from datetime import datetime, timedelta

from alerts.logger import logger
from scrapers.base import BaseClient


class AssetScraperClient(BaseClient):

    """ Finnhub API data forms the base of this client
    """

    def __init__(self):
        super().__init__()

    def get_historical_data(
        self,
        symbol: str = None,
        financial_instrument: str = "Stock",
        date: str = datetime.strftime(
            datetime.now() - timedelta(days=31), "%Y-%m-%d"),
        resolution: int = 30
    ) -> pd.DataFrame:
        ''' Get either historical data for cryptocurrency or stock
        Default entry is to past 1 month data, otherwise, use custom date.

        Parameters
        =============
        symbol -> [str]                 : string
        financial_instrument -> [str]   : Optional, defaults to Stock. Available values include Stock; Cryptocurrency
        date -> [str]                   : Optional %Y-%m-%d, defaults to 31 days before today. 
        resolution -> [int]             : Optional, applies only for Finnhub Stock endpoints. The interval of the data

        Rate Limits
        =============
        ...

        Outputs
        =============
        Iterable[(user, relation_ids, )]        : (defining user detail (user_id or screen_name), relation_ids the returned result from the twitter api)

        Example Usage
        =============
        >>> ...

        Additional Remarks
        =============
        Futures and options data is currently not supported
        '''

        if not financial_instrument:
            raise ValueError(
                "No Financial Instrument Entered. Enter Financial Instrument Type of either 'Stock' or 'Cryptocurrency'")

        financial_instrument = financial_instrument.lower().strip(" ").capitalize()
        if financial_instrument == "Stock":
            return self.retrieve_historical_data(
                ticker=symbol.upper(), resolution=resolution, from_date=date, data_format="csv")
        elif financial_instrument == "Cryptocurrency":
            crypto_client_instance = CoinapiAssetScraperClient()
            return crypto_client_instance.get_crypto_historicaldata(symbol=symbol, from_date=date)
        else:
            raise ValueError(
                "Financial instrument should be either Stock or Cryptocurrency")

    @staticmethod
    def date_to_unixtime(date, datetime_format) -> int:
        """ Return UNIX Time Stamp give a date and datetime format
        Parameters
        =============
        date -> [str]               : date string
        datetime_format -> [str]    : date string date format
        """
        d = datetime.strptime(date, datetime_format)
        unixtime = time.mktime(d.timetuple())
        return int(unixtime)

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

    def retrieve_historical_data(
        self,
        ticker: str,
        from_date: str,
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
        fromdate, todate = self.date_to_unixtime(
            from_date, "%Y-%m-%d"), self.date_to_unixtime(to_date, "%Y-%m-%d")

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
