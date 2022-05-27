import time
import aiohttp
import asyncio
import pandas as pd
from datetime import datetime, timedelta

from app.utils.alerts.logger import logger
from app.utils.alerts.runtime import logruntime
from app.utils.exceptions.wiki_exception import WikipediaExcessiveRequests, WikipediaInvalidPathParameters


class WikipediaScraperClient:

    def __init__(self):

        self.failed_requests = 0

    @logruntime(logger.info)
    async def get_multiple_page_views_mediawiki(
            self,
            past_days: int,
            companies_file_path: str = "../resources/documents/wikipedia/input/companies.csv",
            companies_file_path_col_to_read: str = "companies"):

        ''' Extract wikipedia page views of a csv of companies

        Parameters
        =============
        past_days -> [int]                          : Past how many days to scrape the wikipedia page views data from
        companies_file_path -> [str]                : The path to the csv file containing the name of the companies we want to scrape
        companies_file_path_col_to_read -> [str]    : The column name describing the companies in the csv file for companies_file_path

        Rate Limits
        =============
        Wikipedia states that the web requests are limited to 1000 per minute but have tried 2000 requests in 2s with no issues.

        Outputs
        =============
        Promise[List[pd.DataFrame]]

        Example Usage
        =============
        >>> await get_multiple_page_views_mediawiki(past_days = 30)
        '''

        today = datetime.today()
        start = datetime.today() - timedelta(days=past_days)

        batch_no = 0

        async with aiohttp.ClientSession() as session:

            tasks = []

            try:
                titles = pd.read_csv(companies_file_path)[
                    companies_file_path_col_to_read].unique()
            except:
                raise WikipediaInvalidPathParameters(
                    "Please check that company file path reads to a csv and aligns with the column you are calling from.")

            start_date = start.strftime('%Y%m%d')
            end_date = today.strftime('%Y%m%d')

            for title in titles:

                batch_no += 1

                if batch_no % 100 == 0:  # Send in batches to prevent being rate limited
                    time.sleep(1)

                else:
                    tasks.append(asyncio.ensure_future(
                        self.pageviews_Mediawiki(session, title, start_date, end_date)))

                logger.info(
                    f"Chunk {batch_no} extracted, sleeping for 1s to avoid rate limits... ...")

            tasks_gather = await asyncio.gather(*tasks)

        logger.info(
            f"Extraction completed. Total {self.failed_requests} failed requests.")

        self.failed_requests = 0

        return tasks_gather

    async def get_single_page_views_mediawiki(
            self,
            session,
            title: str,
            start_date: str,
            end_date: str,
            agent: str = "user"):

        ''' Refer to parent get_multiple_page_views_mediawiki for more info
        Parameters
        =============
        title        : string 
        agent        : User agent type, string -> all-agents, user, spider, automated
        start_date   : The date of the first day to include, in YYYYMMDD or YYYYMMDDHH format
        end_date     : The date of the last day to include, in YYYYMMDD or YYYYMMDDHH format
        '''

        url = f"https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/{agent}/{title}/daily/{start_date}/{end_date}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

        try:

            async with session.get(url, headers=headers) as response:

                res = await response.json()

                return res['items']

        except Exception as e:

            self.failed_requests += 1

            if self.failed_requests < 35:

                return logger.warn(f"Request to {title} failed, exception noted to be {e}. Current failed request accumulated at {self.failed_request}.")

            else:

                raise WikipediaExcessiveRequests(
                    f"Too many requests failed, logged {self.failed_requests} failed requests, check calls. Main Exception raised is regarding " + str(e))
