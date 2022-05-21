import os
from dotenv import load_dotenv
load_dotenv()


class BaseClient:

    def __init__(self):
        self.NEWSAPI_APIKEYS_COUNT = 10

        self.NEWSAPI_APIKEYS = [
            os.environ["NEWS_APIKEY_" + str(i)] for i in range(self.NEWSAPI_APIKEYS_COUNT)
        ]
        self.FINNHUB_API_KEY = os.environ["FINNHUB_API_KEY"]
        self.COINAPI_API_KEY = os.environ["COIN_API_KEY"]
        self.USDA_FAS_APIKEY = os.environ["USDA_FAS_API_KEY"]
