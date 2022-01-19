import os
import dotenv
dotenv.load_dotenv()


class BaseClient:

    def __init__(self):
        self.NEWSAPI_APIKEYS_COUNT = 10

        self.NEWSAPI_APIKEYS = [
            os.environ["NEWS_APIKEY_" + str(i)] for i in range(self.NEWSAPI_APIKEYS_COUNT)
        ]
        self.FINHUB_APIKEY = os.environ["FINHUB_APIKEY"]
        self.COINAPI_APIKEY = os.environ["COIN_API_KEY"]
        self.USDA_FAS_APIKEY = os.environ["USDA_FAS_APIKEY"]
