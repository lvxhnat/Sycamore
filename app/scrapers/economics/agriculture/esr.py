import re
import os
import ast
import requests
import datetime
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from app.utils.alerts.logger import logging
load_dotenv()


class ESR:
    """ ESR Data API - United States Weekly Export Sales of Agricultural Commodity Data

    Returns a set of records with Commodity Information. 
    Use it to associate Commodity Name with Commodity Data records obtained by querying Commodity Data End point

    # Reference documentation: https://apps.fas.usda.gov/opendataweb/home
    """

    def __init__(self):

        self.PARAMS = {"API_KEY": os.environ['USDA_FAS_API_KEY']}
        self.url = f"https://apps.fas.usda.gov/OpenData"

        logging.info(
            "Starting up USDA API, requesting base commodities data ... ... ...")

        commodities_response = requests.get(
            url=self.url + "/api/esr/commodities", headers=self.PARAMS)
        commodities_for_query = pd.DataFrame.from_dict(
            ast.literal_eval(commodities_response.text))

        logging.info("Available Commodities for Query: \n\n" +
                     " | ".join(list(commodities_for_query.commodityName.unique())))

        self.commodity_name_to_id = commodities_for_query.set_index(
            "commodityName")[['commodityCode']].to_dict()['commodityCode']
        self.commodity_id_to_name = commodities_for_query.set_index(
            "commodityCode")[['commodityName']].to_dict()['commodityName']

    def get_commodity_id(self, commodity) -> np.int64:
        """ Retrieve commodity id that we can use for querying given the name of the agricultural product
        Parameters
        ----------    
        commodity    : The commodity name based on the printed possible available inputs given above 

        Example Usage
        ----------   
        >>> commodity = ESR()
        >>> commodity.get_commodity_id('Corn')
        401 
        """

        return self.commodity_name_to_id[commodity]

    def available_countries_for_query(self) -> pd.DataFrame:
        """ Returns a set of records with Countries and their corresponding Regions Codes the Country belongs to. 
        Use it to associate Country Name with Commodity Data records obtained by querying Commodity Data End point.

        Example Usage
        ----------   
        >>> commodity = ESR()
        >>> commodity.available_countries_for_query().head()

        countryCode	 countryName	countryDescription	    regionId	gencCode
        1	          EUROPEAN	    EUROPEAN UNION - 27	        1	      null
        2	           UNKNOWN	         UNKNOWN	            99	       AX1
        1010	       GREENLD	        GREENLAND               11	       GRL
        1220	        CANADA	          CANADA                11	       CAN
        1610	        MIGUEL	   ST. PIERRE AND MIQUELON      11	      null
        ...
        """

        countries_endpoint = "/api/esr/countries"

        countries_response = requests.get(
            url=self.url + countries_endpoint, headers=self.PARAMS).text

        return pd.DataFrame.from_dict(ast.literal_eval(countries_response.replace("null", '"null"')))

    def countries_export_to_usa(self,
                                commodity_code: int,
                                market_year: int = datetime.datetime.now().year) -> pd.DataFrame:
        """ Given Commodity Code (Ex: 104 for Wheat - White ) and market year (Ex: 2017) this API End point will return a list of US Export records of White Wheat to all applicable countries from USA for the given Market Year. 
        Please see DataReleaseDates end point to get a list of all Commodities and the corresponding Market Year data.
        || HIGHLIGHT: These numbers are export records of commodity to applicable countries **

        Data Release Frequency: Bi-Weekly

        Parameters
        ----------    
        commodity_code    : commodity code
        market_year       : year we want, 2019, 2020, 2021

        Output
        ----------   
        Output       : pandas dataframe; containing 'commodity', 'commodityCode', 'country', 'countryCode', 'weeklyExports', 'accumulatedExports','outstandingSales', 'grossNewSales', 'currentMYNetSales', 'currentMYTotalCommitment', 'nextMYOutstandingSales', 'nextMYNetSales', 'unitId', 'weekEndingDate'

        Example Usage
        ----------   
        >>> commodity = ESR()
        >>> commodity.countries_export_to_usa(commodityCode = 401)

        commodity	commodityCode	country			countryCode		weeklyExports	accumulatedExports	outstandingSales	grossNewSales	currentMYNetSales	currentMYTotalCommitment	nextMYOutstandingSales	nextMYNetSales	unitId			date
            Corn		401			CANADA				1220			5599			5599				84173				36095			-7244					89772							0					0			1		2019-09-05
            Corn		401			MEXICO				2010			212010			212010				3407428				495420			193847					3619438							60000				0			1		2019-09-05
            Corn		401			GUATEMALA			2050			0				0					314990				20931			7564					314990							0					0			1		2019-09-05
            Corn		401			EL SALVADOR			2110			0				0					85254				15300			10235					85254							0					0			1		2019-09-05
            Corn		401			HONDURAS			2150			28435			28435				171196				54530			32274					199631							0					0			1		2019-09-05
        ...

        || NOTES: currentMYTotalCommitment - Signed Contracts for buying the commodity 
        """

        availableCountries = self.available_countries_for_query()
        mapCountries = availableCountries.set_index(
            "countryCode")[['countryDescription']].to_dict()['countryDescription']

        countriesExport_endpoint = f"/api/esr/exports/commodityCode/{commodity_code}/allCountries/market_year/{market_year}"

        export_response = requests.get(
            url=self.url + countriesExport_endpoint, headers=self.PARAMS).text

        exportsdf = pd.DataFrame(ast.literal_eval(export_response))

        exportsdf['commodity'] = exportsdf.commodityCode.apply(
            lambda x: self.commodity_id_to_name[x])
        exportsdf['country'] = exportsdf.countryCode.apply(
            lambda x: mapCountries[x])
        exportsdf = exportsdf[['commodity', 'commodityCode', 'country', 'countryCode', 'weeklyExports', 'accumulatedExports', 'outstandingSales',
                               'grossNewSales', 'currentMYNetSales', 'currentMYTotalCommitment', 'nextMYOutstandingSales', 'nextMYNetSales', 'unitId', 'weekEndingDate']]

        exportsdf.country = exportsdf.country.apply(
            lambda x: x.strip())  # Formatting dates and country spacing
        exportsdf['date'] = exportsdf.weekEndingDate.apply(
            lambda x: datetime.datetime.strptime(re.findall("....-..-..", x)[0], "%Y-%m-%d"))
        exportsdf = exportsdf.drop(columns=['weekEndingDate'])

        return exportsdf

    def country_export_to_usa(self,
                              country_code: int,
                              commodity_code: int,
                              market_year: int = datetime.datetime.now().year) -> pd.DataFrame:
        """Given Commodity Code (Ex: 104 for Wheat - White ), Country Code (Ex:1220 for Canada) and market_year (Ex: 2017) this API End point will return a list of US Export records of White Wheat to Canada from USA for the give Market Year. Please see DataReleaseDates end point to get a list of all Commodities and the corresponding Market Year data.

        || HIGHLIGHT: These numbers are export records of commodity to applicable countries **

        Data Release Frequency: Bi-Weekly

        Parameters
        ----------    
        commodity_code    : commodity code
        country_code      : country code, see .available_countries_for_query()
        market_year       : year we want, 2019, 2020, 2021

        """
        availableCountries = self.available_countries_for_query()
        mapCountries = availableCountries.set_index(
            "countryCode")[['countryDescription']].to_dict()['countryDescription']

        countryExport_endpoint = f"/api/esr/exports/commodityCode/{commodity_code}/countryCode/{country_code}/market_year/{market_year}"

        export_response = requests.get(
            url=self.url + countryExport_endpoint, headers=self.PARAMS).text

        exportsdf = pd.DataFrame(ast.literal_eval(export_response))
        exportsdf['commodity'] = exportsdf.commodityCode.apply(
            lambda x: self.commodity_id_to_name[x])
        exportsdf['country'] = mapCountries[country_code]

        exportsdf.country = exportsdf.country.apply(
            lambda x: x.strip())  # Formatting dates and country spacing
        exportsdf['date'] = exportsdf.weekEndingDate.apply(
            lambda x: datetime.datetime.strptime(re.findall("....-..-..", x)[0], "%Y-%m-%d"))
        exportsdf = exportsdf.drop(columns=['weekEndingDate'])

        exportsdf = exportsdf[['date', 'commodity', 'commodityCode', 'country', 'countryCode', 'weeklyExports', 'accumulatedExports',
                               'outstandingSales', 'grossNewSales', 'currentMYNetSales', 'currentMYTotalCommitment', 'nextMYOutstandingSales', 'nextMYNetSales', 'unitId']]

        return exportsdf
