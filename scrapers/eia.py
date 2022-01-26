import requests
import pandas as pd
from bs4 import BeautifulSoup


class EIAScraperClient:
    ''' Scraper for US Energy Information Administration
    '''

    def __init__(self):
        pass

    def get_weekly_ethanol_production_levels(self):
        ''' Get the weekly ethanol production levels in continental united states

        Outputs
        =============
        pd.DataFrame

        Example Usage
        =============
        >>> get_weekly_ethanol_production_levels()
            date	value
        0	2010-06-04	839
        0	2010-06-11	839
        0	2010-06-18	846
        0	2010-06-25	832
                ...
        '''
        df = self.base_ethanol_scraper(
            "https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=pet&s=w_epooxe_yop_nus_mbbld&f=w").applymap(lambda x: x.replace(",", ""))
        df.reset_index(drop=True, inplace=True)
        return df

    def get_weekly_ethanol_ending_stocks(self):
        ''' Get the weekly ethanol storage stock in continental united states

        Outputs
        =============
        pd.DataFrame

        Example Usage
        =============
        >>> get_weekly_ethanol_ending_stocks()
                date	value
        0	2010-06-04	18309
        0	2010-06-11	18551
        0	2010-06-18	19368
        0	2010-06-25	19499
        1	2010-07-02	19921

        '''
        df = self.base_ethanol_scraper(
            "https://www.eia.gov/dnav/pet/hist/LeafHandler.ashx?n=PET&s=W_EPOOXE_SAE_NUS_MBBL&f=W").applymap(lambda x: x.replace(",", ""))
        df.reset_index(drop=True, inplace=True)
        return df

    def base_ethanol_scraper(self, url):
        ''' For usage guidelines, refer to the top two get_ methods
        '''

        try:
            response = requests.get(url).text

            soup = BeautifulSoup(response)

            data = []
            table_body = soup.find('tbody')

            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                data.append([ele for ele in cols if ele])

            columns = ['year-month', 'week1_enddate', 'week1_value', 'week2_enddate', 'week2_value',
                       'week3_enddate', 'week3_value', 'week4_enddate', 'week4_value', 'week5_enddate', 'week5_value']
            ethanol = pd.DataFrame(data, columns=columns).dropna(
                subset=['year-month'])

            ethanol['year'] = ethanol['year-month'].apply(
                lambda x: x.split("-")[0])
            ethanol['month'] = ethanol['year-month'].apply(
                lambda x: x.split("-")[1])

            weeks_col = ['week1_enddate', 'week2_enddate',
                         'week3_enddate', 'week4_enddate', 'week5_enddate']

            data = []
            for week in weeks_col:
                ethanol[week] = ethanol[week].apply(
                    lambda x: "-".join(x.split("/")) if x != None else x)
                ethanol[week] = ethanol['year'] + "-" + ethanol[week]
                ethanolItem = ethanol[[week, week.replace("enddate", "value")]]
                data.append(ethanolItem.rename(
                    columns={week.replace("_enddate", "_value"): "value", week: "date"}))

            fuelethanol_production = pd.concat(
                data).dropna().sort_values("date")

            return fuelethanol_production

        except:
            return None
