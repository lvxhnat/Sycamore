import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime


def CryptoHistoricalData_GEMINIAPI(symbol: str = "btcusd"):
    """
    Retrieve Past 1 Month Data from Gemini, with 30 minutes time interval

    Rate Limit 
    ======================
    120 requests per minute 

    Symbols Available
    ======================
     'btcusd', 'ethbtc',
     'ethusd', 'zecusd', 'zecbtc', 'zeceth', 'zecbch', 'zecltc', 'bchusd', 'bchbtc',
     'bcheth', 'ltcusd', 'ltcbtc', 'ltceth', 'ltcbch', 'batusd', 'daiusd', 'linkusd',
     'oxtusd', 'batbtc', 'linkbtc', 'oxtbtc', 'bateth', 'linketh', 'oxteth','ampusd',
     'compusd', 'paxgusd', 'mkrusd', 'zrxusd', 'kncusd', 'manausd', 'storjusd', 'snxusd', 
     'crvusd', 'balusd', 'uniusd', 'renusd', 'umausd', 'yfiusd', 'btcdai', 'ethdai',
     'aaveusd', 'filusd', 'btceur', 'btcgbp', 'etheur', 'ethgbp', 'btcsgd', 'ethsgd',
     'sklusd', 'grtusd', 'bntusd', '1inchusd', 'enjusd', 'lrcusd', 'sandusd',
     'cubeusd', 'lptusd', 'bondusd', 'maticusd', 'injusd', 'sushiusd',
     'dogeusd', 'alcxusd', 'mirusd', 'ftmusd', 'ankrusd', 'btcgusd', 'ethgusd',
     'ctxusd', 'xtzusd', 'axsusd', 'slpusd', 'lunausd', 'ustusd', 'mco2usd'

    """

    cryptoitem = requests.get(
        f"https://api.gemini.com/v2/candles/{symbol}/30m").text
    cryptosymbol = pd.DataFrame(ast.literal_eval(cryptoitem), columns=[
                                'time', 'open', 'high', 'low', 'close', 'volume'])
    cryptosymbol.time = cryptosymbol.time.apply(
        lambda x: datetime.fromtimestamp(x/1000.0))

    return cryptosymbol


def stringToLargeLiteral(strnum):
    """ Clean M, B, T from string and convert to large integer
    """

    if "M" in strnum:

        return int(float(strnum.replace("M", "")) * 1000000)

    elif "B" in strnum:

        return int(float(strnum.replace("B", "")) * 1000000000)

    elif "T" in strnum:

        return int(float(strnum.replace("T", "")) * 1000000000)


def MarketCapitalisation_YCHARTSAPI(ticker):
    """ Get the market capitalisation based on the stock ticker
    ticker     : str
    """

    def checkLargeNumber(num):

        try:

            if float(num) > 50000:

                return True

            else:

                return False

        except Exception as e:

            return False

    url = f'https://ycharts.com/companies/{ticker}/market_cap'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, features="lxml")

    data = []

    rows = soup.find_all('tr')

    for row in rows:

        cols = row.find_all('td')

        cols = [ele.text.strip() for ele in cols]

        try:

            if str(datetime.now().year) in cols[0]:

                q = []

                for ele in cols:

                    if any(ext in ele for ext in ["M", "B", "T"]) or checkLargeNumber(ele):

                        q.append(ele)

                data.append(q)  # Get rid of empty values

        except:

            pass

    return data
