from scrapers.base import BaseClient
from utils.alerts.logger import logger
from utils.alerts.typeprompts import NASSCropProductionInfo
import re
import sys
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

sys.path.append("...")


class USDAScraperClient(BaseClient):
    ''' Scraper for US Department of Agriculture
    '''

    def __init__(self):
        super().__init__(self)

    def get_agency_reports(self) -> pd.DataFrame:
        ''' USDA Scheduled Release Dates for all Agency Reports and Summaries
        Data is released based on Eastern Time (ET) 
        ------------------------------------------------
        FREQUENCY : DAILY
        ------------------------------------------------

        Outputs
        =============
        pd.DataFrame

        Example Usage
        =============
        >>> get_agency_reports()
        release_date	report	link	time	agency
        0	2021-12-23 Eastern Time (ET)	Weekly Export Sales	https://www.fas.usda.gov/programs/export-sales...	8:30 am	FAS
        1	2021-12-23 Eastern Time (ET)	Cattle on Feed	https://www.nass.usda.gov/Publications/Calenda...	3:00 pm	NASS
        ... ...
        '''

        try:
            soup = BeautifulSoup(requests.get(
                "https://www.usda.gov/media/agency-reports").text, "lxml")

            tag_dates = soup.find_all(lambda tag: tag.name == 'h3' and str(
                datetime.now().year) in tag.get_text())
            tag_dates = [re.findall(">(.*?)<", str(tag_date))[0]
                         for tag_date in tag_dates]

            agency_reports = soup.find_all("ul", {"class": "agency-reports"})

            # Make sure they are of the same length or might result in a misalignment when put to dataframe
            assert(len(agency_reports) == len(tag_dates))

            agency_calendars_df = []

            for tag_date, agencyReport in zip(tag_dates, agency_reports):
                for li in agencyReport.find_all("li"):
                    report_name = re.findall(
                        '>(.*?)<', str(li.find_all("a")))[0]
                    link_to_report = re.findall(
                        'href="(.*?)"', str(li.find_all("a", href=True)[0]))[0]
                    agency_report_date = re.findall(
                        '>(.*?)<', str(li.find_all("span", {"class": "agency-report-date"})))[0]
                    agency = re.findall(
                        '>(.*?)<', str(li.find_all("span", {"class": "agency-report-agency"})))[0]

                    agency_calendars_df.append(
                        (tag_date, report_name, link_to_report, agency_report_date, agency))

            agency_calendars_df = pd.DataFrame(agency_calendars_df, columns=['release_date', 'report', 'link', 'time', 'agency']).applymap(
                lambda x: x.replace("\t", "").replace("\n", "").strip(" "))
            agency_calendars_df.release_date = agency_calendars_df.release_date.apply(lambda x: datetime.strftime(
                datetime.strptime(x, "%a, %m/%d/%Y"), "%Y-%m-%d") + " Eastern Time (ET)")

            return agency_calendars_df

        except:
            return None

    def get_crop_production_reports(self) -> NASSCropProductionInfo:
        ''' This USDA monthly report contains crop production data for the U.S., including acreage, area harvested, and yield. 
        Wheat, fruits, nuts, and hops are the specific crops included in the report, but data on planted and harvested crop area are also included. 
        There is also a strong focus on maple syrup, as the report details production, value, season dates, and percent of sales by type. 
        The report also contains a monthly weather summary, a monthly agricultural summary, and an analysis of precipitation and the degree of departure from the normal precipitation map for the month.
        ------------------------------------------------
        FREQUENCY : BETWEEN 9-12 MONTHLY 12:00 PM Eastern Time (ET)
        ------------------------------------------------
        Link: https://usda.library.cornell.edu/concern/publications/tm70mv177?locale=en

        Outputs
        =============
        attr_freq            : str ; The frequency release type, i.e. Monthly, Weekly, Annual (In this case, Monthly)
        attr_upcomingRelease : list ; The Upcoming release dates
        hrefs                : pd.DataFrame ; Pandas Dataframe containing PDF, TXT, ZIP report urls

        Example Usage
        =============
        >>> get_crop_production_reports()
        {'frequency': 'Monthly', 
         'upcoming_dates': ['Jan 12 2022 12:00 PM',
                            'Feb  9 2022 12:00 PM',
                            'Mar  9 2022 12:00 PM',
                            'Apr  8 2022 12:00 PM',
                            'May 12 2022 12:00 PM',
                            ...
                            ],
         'df': 
                pdf	txt	zip
            0	https://downloads.usda.library.cornell.edu/usd...	https://downloads.usda.library.cornell.edu/usd...	https://downloads.usda.library.cornell.edu/usd...
            1	https://downloads.usda.library.cornell.edu/usd...	https://downloads.usda.library.cornell.edu/usd...	https://downloads.usda.library.cornell.edu/usd...
            2	https://downloads.usda.library.cornell.edu/usd...	https://downloads.usda.library.cornell.edu/usd...	https://downloads.usda.library.cornell.edu/usd...
        }
        '''

        try:
            soup = BeautifulSoup(requests.get(
                "https://usda.library.cornell.edu/concern/publications/tm70mv177?locale=en").text, "lxml")

            attr_upcoming_release = soup.find_all(
                "span", {"class": "attribute upcoming_releases"})
            attr_upcoming_release = [re.findall(
                ">(.*?)<", str(attr_ur))[0] for attr_ur in attr_upcoming_release]

            attr_freq = soup.find_all(
                "span", {"class": "attribute frequency"})[0]
            attr_freq = re.findall(">(.*?)<", str(attr_freq))[0]

            table = soup.find_all("table")[0]
            hrefs = np.array([re.findall('href="(.*?)"', str(a))[0]
                              for a in table.find_all('a', href=True)])
            hrefs = pd.DataFrame(np.array_split(hrefs, int(len(hrefs)/4)),
                                 columns=['pdf', 'txt', 'zip', 'drop']).drop(columns=['drop'])

            return {
                'frequency': attr_freq,
                'upcoming_dates': attr_upcoming_release,
                'df': hrefs
            }

        except:
            return None
