import os
import sys
import dotenv

sys.path.append("...")

from alerts.logger import logger
from scrapers.base import BaseClient
from utils.cleaning_utils import textualtime_to_timestring

import warnings
import re
import requests
import pandas as pd
import dateutil.parser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

import warnings
warnings.filterwarnings("ignore")


dotenv.load_dotenv()


warnings.filterwarnings("ignore")


class NewsScraperClient(BaseClient):

    def __init__(self):

        super().__init__(self)
        self.APIKEY = self.NEWSAPI_APIKEYS[0]

        self.key_state = 0

    def get_newsapi_articles(
            self,
            date: str = None,
            pageSize: int = 100,
            sort: str = "publishedAt",
            language: str = "en",
            query: str = "newsapi_agriculture_query.txt") -> pd.DataFrame:
        ''' 
        News API endpoint to get live news data crawled from google webpages https://newsapi.org/docs/endpoints/everything

        Surround phrases with quotes (") for exact match.
        Prepend words or phrases that must appear with a + symbol. Eg: +bitcoin
        Prepend words that must not appear with a - symbol. Eg: -bitcoin
        Alternatively you can use the AND / OR / NOT keywords, and optionally group these with parenthesis. Eg: crypto AND (ethereum OR litecoin) NOT bitcoin.

        This endpoint ONLY gets the news data for the current day

        Parameters
        =============
        date -> [str]           : %Y-%m-%d , toggled as both start and end dates
        pageSize -> [int]       : page size, defaults to 100 (max) for result page
        sort -> [str]           : sort order, relevancy, popularity, publishedAt. Defaults to publishedAt
        language -> [str]       : two letter ISO language code, for language of the news articles
        query -> [str]          : query string, as in those in query languages with OR and AND operators. Allows option of either the direct query string, or the file name being searched in the resources/queries directory

        Rate Limits
        =============
        100 requests per day per api key. 1000 requests/day with our API key capacity.

        Outputs
        =============
        Pandas dataframe

        Example Usage
        =============
        >>> ...

        '''

        # Makes sure that its converted to Eastern Time (ET)
        if not date:
            date = datetime.strftime(
                datetime.now() - timedelta(hours=8), "%Y-%m-%d")
        else:
            date = datetime.strftime(datetime.strptime(
                date, "%Y-%m-%d") - timedelta(hours=8), "%Y-%m-%d")

        START = END = date

        if ".txt" in query:
            query = "../resources/queries/" + query.replace("/", "")
            with open(query) as file:
                query = file.readlines()
        # Commodity Query

        response = requests.get(
            f"https://newsapi.org/v2/everything?qInTitle={query}&language={language}&apiKey={self.APIKEY}&from={START}&to={END}&sortBy={sort}&pageSize={pageSize}").text

        responseEval = eval(response.replace("null", "''"))

        if responseEval['status'] == "ok":
            q = pd.DataFrame(responseEval['articles'])
            q["UTC"] = q.publishedAt.apply(lambda x: datetime.strftime(
                dateutil.parser.parse(x), "%Y-%m-%d %H:%M:%S"))
            q["SGT"] = q.publishedAt.apply(lambda x: datetime.strftime(
                dateutil.parser.parse(x) + timedelta(hours=8), "%Y-%m-%d %H:%M:%S"))

            q.source = q.source.apply(lambda x: x['name'])
            for column in ["title", "description", "content"]:
                q[column] = q[column].apply(lambda x: re.sub('<.*>', '', x).replace(
                    u'\xa0', u' ').replace("\n", " .").replace("\r", "").replace("\t", " "))

            return q.drop(columns=["publishedAt", "urlToImage"])

        elif responseEval['status'] == "error":

            self.key_state += 1

            APIKEY = os.environ["APIKEY_" + str(self.key_state)]

            if self.key_state < len(self.NEWSAPI_APIKEYS):

                return self.NewsData()

            else:

                logger.error("Exhausted all API Keys")

    def get_agricensus_headlines() -> pd.DataFrame:
        ''' Returns Headlines from the agricensus website, 
        Link: https://www.agricensus.com/news/

        Outputs
        =============
        Pandas dataframe

        Example Usage
        =============
        >>> get_agricensus_headlines()
            title	url	time_before	description	source	author
        0	Iran's SLAL rumored buying 300kmt corn, GTC - ...	/Article/Iran-s-SLAL-rumored-buying-300kmt-cor...	2021-12-24 07:53:48	Iran’s state-owned Government Trading Corporat...	Agricensus	Agricensus
        1	Arg. November bean crush drops 13% on negative...	/Article/Arg-November-bean-crush-drops-13-on-n...	2021-12-24 07:19:48	Soybean crush in Argentina dropped 13% on the ...	Agricensus	Agricensus
        2	US corn net sales down 50% at 982k mt, exports...	/Article/US-corn-net-sales-down-50-at-982k-mt-...	2021-12-24 07:19:48	US corn net sales in the week to December 16 w...	Agricensus	Agricensus

        '''

        try:
            agricensus_headlines = BeautifulSoup(requests.get(
                "https://www.agricensus.com/news/").text, features="html.parser").find_all("div", {"class": "news-list-block shadow-box"})

            agricensus_page1_data = []

            for headline in agricensus_headlines:

                title = headline.find_all("div", {"class": "news-list-title"})
                auth = headline.find_all(
                    "div", {"class": "news-list-date-author"})
                desc = headline.find_all(
                    "div", {"class": "news-list-description"})

                url_items = headline.select("a[href*=Article]")
                url = [re.findall("href=\"(.*?)\"", str(url_item))[0]
                       for url_item in url_items][0]

                title_clean = [i for i in re.findall(
                    ">(.*?)<", str(title[0])) if i != ""][0]
                auth_clean = [i for i in re.findall(
                    ">(.*?)<", str(auth[0])) if i != ""][0].replace("|", "").strip(" ")
                desc_clean = [i for i in re.findall(
                    ">(.*?)<", str(desc[0])) if i != ""][0]
                agricensus_page1_data.append(
                    (title_clean, url, auth_clean, desc_clean))

            a = pd.DataFrame(agricensus_page1_data, columns=[
                'title', 'url', 'time_before', 'description'])

            a.time_before = a.time_before.apply(
                lambda x: textualtime_to_timestring(x))  # Process time strings

            a['source'] = "Agricensus"
            a['author'] = "Agricensus"
            a = a.fillna("")

            return a

        except:
            return None
