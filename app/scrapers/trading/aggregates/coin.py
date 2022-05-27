import re
import requests
import pandas as pd

from app.utils.alerts.logger import logger
from app.scrapers.base import BaseClient


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
