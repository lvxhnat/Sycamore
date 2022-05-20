import pandas as pd
from scrapers.trading.alphavantage import AlphaVantageClient
from scrapers.trading.finnhub import FinnhubClient


class TradingDataClient:

    def __init__(self, ):
        self.finnhub_client = FinnhubClient()
        self.alphavantage_client = AlphaVantageClient()

    def get_historical_data(
        self,
        ticker: str,
        from_date: str,
        to_date: str = "2022-02-20",
        resolution: str = "1D",
        instrument: str = "stock",
    ) -> pd.DataFrame:
        """ Get historical ticker data.

        Parameters
        =============
        ticker -> [str]     : The ticker symbol 
        from_date -> [str]  : %Y-%m-%d 
        to_date -> [str]    : %Y-%m-%d
        resolution -> [str] : Supported resolutions are - 
                              MINUTE: 1MIN, 5MIN, 15MIN, 30MIN, 
                              HOUR: 1H
                              DAY: 1D, 5D, 15D, 30D, 60D
                              WEEK: 1W, 5W, 15W, 30W, 60W
                              MONTH: 1M, 5M, 15M, 30M, 60M


        """
        finnhub_supported_intervals = ["1MIN", "5MIN", "15MIN", "30MIN", "1H"]
        alphavantage_supported_intervals = [
            "1D", "5D", "15D", "30D", "60D", "1W", "5W", "15W", "30W", "60W", "1M", "5M", "15M", "30M", "60M"]

        instrument = instrument.strip(" ").lower()
        resolution = resolution.strip(" ").upper()

        if resolution in finnhub_supported_intervals:
            historical_data = self.finnhub_client.get_historical_data(
                ticker, resolution, from_date)
        elif resolution in alphavantage_supported_intervals:
            historical_data = self.alphavantage_client.get_historical_data(
                ticker, resolution, from_date)
        else:
            raise ValueError(
                "Resolution is not supported. Please check documentation for list of supported resolutions.")

        return historical_data
