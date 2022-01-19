from datetime import datetime, timedelta
import pandas as pd
import requests
import time
import re

from sycamore.alerts.logger import logger
from sycamore.scrapers.base import BaseClient


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


class CoinapiAssetScraperClient(BaseClient):

    def __init__(self):
        super().__init__(self)

    def get_cryptoexchange_symbols(
            self,
            symbol: str = "OKEX") -> pd.DataFrame:
        """ Get all of the cryptocurrencies listed on the exchange
        Full list of exchanges available in a separate endpoint, can be crosschecked and added here. Docs: https://docs.coinapi.io/#list-all-exchanges-get

        Parameters
        =============
        symbol -> [str]         : cryptocurrency exchange name string

        Rate Limits
        =============
        3 requests per second, up to 6 requests per second in bursts
        """

        url = f'https://rest.coinapi.io/v1/symbols?filter_exchange_id={symbol}'
        headers = {'X-CoinAPI-Key': self.COINAPI_APIKEY}
        response = requests.get(url, headers=headers)

        symbols = eval(response.text.replace(
            "true,", "'',").replace("false,", "'',"))
        symbols = pd.DataFrame(symbols)

        spot_symbols = symbols[(symbols.symbol_type == "SPOT")
                               & (symbols.asset_id_quote == "USDT")]

        return spot_symbols

    def get_crypto_historicaldata(
            self,
            symbol: str = "BTC",
            period: str = "30MIN",
            from_date: str = "2021-09-01",
            limit: int = 100000) -> pd.DataFrame:
        """

        Parameters
        =============
        symbol -> [str]     : 'GAS', 'NEO', 'ETH', 'BCH', 'QTUM', 'ETC', 'LTC', 'BTC', 'MKR', 'DNA', 'PPT', 'VIB', 'UBTC', 'MDT', 'MCO', 'MDA', 'ARK', 'BNT', 'NULS', 'AST', 'TRUE', 'THETA', 'XEM', 'TCT', 'ZRX', 'XMR', 'CVC', 'LINK', 'PAY', 'WTC', 'ZEC', 'ICX', 'NAS', 'YOYOW', 'YEE', 'OMG', 'KNC', 'FAIR', 'STORJ', 'XLM', 'ELF', 'MOF', 'DGB', 'ITC', 'UTK', 'TOPC', 'RNT', 'COMET', 'DASH', 'KCASH', 'BTG', 'INT', 'SNT', 'LRC', 'IOTA', 'MANA', 'TRX', 'PST', 'SWFTC', 'XUC', 'AAC', 'BTM', 'ACT', 'IOST', 'BCD', 'EOS', 'XRP', 'SOC', 'ZEN', 'NANO', 'GTO', 'CHAT', 'MITH', 'ABT', 'TRIO', 'TRA', 'REN', 'QUN', 'ENJ', 'ONT', 'OKB', 'CTXC', 'ZIL', 'YOU', 'LSK', 'LBA', 'AE', 'SC', 'KAN', 'DCR', 'WAVES', 'ORST', 'CVT', 'EGT', 'LET', 'ADA', 'HYC', 'USDC', 'PAX', 'GUSD', 'TUSD', 'GNT', 'HMCN', 'BCHSV', 'LEND', 'BTT', 'ZIP', 'BEC', 'BLOC', 'ATOM', 'EDO', 'ALV', 'LAMB', 'ETM', 'LEO', 'ALGO', 'CRO', 'WXT', 'FTM', 'DGD', 'STC', 'DOGE', 'ORBS', 'FSN', 'EM', 'EC', 'RFR', 'R', 'BKX', 'PLG', 'VSYS', 'SHOW', 'PRA', 'XPO', 'INSUR', 'HBAR', 'SSC', 'LIGHT', 'OF', 'UGC', 'IPC', 'CIC', 'INS', 'DPY', 'HMC', 'MOT', 'XTZ', 'ROAD', 'DAI', 'XAS', 'HPB', 'CAI', 'RVN', 'WIN', 'APM', 'HDAO', 'MVP', 'BAT', 'DADI', 'OXT', 'DEP', 'CTC', 'NDN', 'BHP', 'WGRT', 'IQ', 'TMTG', 'COMP', 'APIX', 'DMG', 'CELO', 'DOT', 'AERGO', 'SNX', 'BAL', 'XSR', 'ANT', 'CRV', 'SRM', 'XPR', 'DIA', 'PNK', 'OM', 'YFI', 'JST', 'TRB', 'RSR', 'BAND', 'WNXM', 'YFII', 'UMA', 'SUSHI', 'CVP', 'KSM', 'TRADE', 'JFI', 'TAI', 'SWRV', 'KLAY', 'SUN', 'REP', 'NMR', 'MLN', 'ZYRO', 'WBTC', 'FRONT', 'WING', 'RIO', 'UNI', 'DHT', 'CNTM', 'AVAX', 'INX', 'DMD', 'BOX', 'MXT', 'ANW', 'FLM', 'RFUEL', 'SFG', 'EGLD', 'SOL', 'GHST', 'MEME', 'HSR', 'EXE', 'POE', 'OST', 'REQ', 'AAVE', 'SNC', 'RCN', 'EVX', 'HOPL', 'LMCH', 'AIDOC', 'ENG', 'ACE', 'CAN', 'SALT', 'FUN', 'SNGLS', 'RDN', 'TNB', 'UCT', 'AMM', 'VALUE', 'SPF', 'CAG', 'LEV', 'OAX', 'QVT', 'ICN', 'DNT', 'KEY', 'SAN', 'DAT', '1ST', 'GNX', 'WRC', 'MAG', 'DENT', 'GSC', 'NEAR', 'FIL', 'OK06ETT', 'KP3R', 'PICKLE', 'COVER', 'API3', 'HEGIC', 'VIU', 'NU', 'LOON', 'VNT', 'MTH', 'BRD', 'SUB', 'METAL', 'NGC', 'UKG', 'ATL', 'REF', 'GRT', 'AVT', 'VEE', 'RCT', 'LON', 'BETH', '1INCH', 'CBT', 'BADGER','BCHA', 'OKT', 'AUTO', 'PHA', 'POLS', 'MXC', 'PROPS', 'PRQ', 'MIR', 'GLM', 'TORN', 'FLOW', 'TIO', 'LUNA', 'MASK', 'SNM', 'LA', 'READ', 'CFX', 'CHZ', 'ALPHA', 'STX', 'VELO', 'PERP', 'WFEE', 'KINE', 'BOT', 'ANC', 'SAND', 'DORA', 'CONV', 'CELR', 'MATIC', 'SKL', 'ZKS', 'LPT', 'KONO', 'AUCTION', 'GAL', 'CEL', 'DAO', 'GTC', 'FORTH', 'EDGE', 'VRA', 'XCH', 'CSPR', 'SHIB', 'ICP', 'LAT', 'STRK', 'KISHU', 'AKITA', 'MINA', 'BCN', 'BZZ', 'CQT', 'SMT', 'FEG', 'CFG', 'CTR', 'XEC', 'KAR', 'AXS', 'YFV', 'YGG', 'CLV', 'OMI', 'EFI', 'BABYDOGE', 'WNCG', 'SLP', 'ERN', 'REVV', 'USDK', 'BCHABC', 'AGLD', 'ILV', 'DYDX', 'CGS', 'EDEN', 'MON', 'GALA', 'CHE'
        period -> [str]     :
        Second	1SEC, 2SEC, 3SEC, 4SEC, 5SEC, 6SEC, 10SEC, 15SEC, 20SEC, 30SEC
        Minute	1MIN, 2MIN, 3MIN, 4MIN, 5MIN, 6MIN, 10MIN, 15MIN, 20MIN, 30MIN
        Hour	1HRS, 2HRS, 3HRS, 4HRS, 6HRS, 8HRS, 12HRS
        Day	    1DAY, 2DAY, 3DAY, 5DAY, 7DAY, 10DAY
        Month	1MTH, 2MTH, 3MTH, 4MTH, 6MTH
        Year	1YRS, 2YRS, 3YRS, 4YRS, 5YRS
        from_date -> [str]  : %Y-%m-%d - date to scrape from

        Rate Limit 
        =============
        3 requests per second, up to 6 requests per second in bursts

        Additional Remarks
        =============
        Amount of items to return (optional, mininum is 1, maximum is 100000, default value is 100
        If the parameter is used then every 100 output items are counted as one request)

        """
        timestart = from_date + "T00:00:00"
        ticker = "OKEX_SPOT_" + symbol + "_USDT"

        url = f'https://rest.coinapi.io/v1/ohlcv/{ticker}/history?period_id={period}&time_start={timestart}&limit={limit}'
        headers = {'X-CoinAPI-Key': self.COINAPI_APIKEY}

        try:

            response = requests.get(url, headers=headers)

            data = pd.DataFrame(eval(response.text)).drop(columns=['time_period_start', 'time_open', 'time_close']).rename(columns={
                "time_period_end": "date",
                "price_open": "open",
                "price_close": "close",
                "price_low": "low",
                "price_high": "high",
                "volume_traded": "volume",
                "trade_count": "trades"})

            data.date = data.date.apply(lambda x: re.findall(
                "....-..-..T..:..:..", x)[0].replace("T", " "))

        except:

            logger.error(
                "Errored out while retriving historical crypto prices from coin API")

        return data
