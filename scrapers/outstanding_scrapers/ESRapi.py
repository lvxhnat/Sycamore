import ast
import json
import re
import os
from numpy.core.arrayprint import ComplexFloatingFormat
import requests
import datetime
import numpy as np
import pandas as pd
from dotenv import load_dotenv
load_dotenv()


# Python Wrapper for - https://apps.fas.usda.gov/opendataweb/home

# ---------------------------------------------
# IMPORT USDA Credentials here
APIKEY = os.environ['USDA_FAS_APIKEY']
# ---------------------------------------------


class ESR:

    r""" ESR Data API - United States Weekly Export Sales of Agricultural Commodity Data

    Returns a set of records with Commodity Information. 
    Use it to associate Commodity Name with Commodity Data records obtained by querying Commodity Data End point

    """

    def __init__(self, APIKEY=APIKEY):

        self.PARAMS = {"API_KEY": APIKEY}
        self.url = f"https://apps.fas.usda.gov/OpenData"

        commodities_endpoint = "/api/esr/commodities"

        ## logger.info("Starting up USDA API, requesting base commodities data ... ... ...")
        commodities_response = requests.get(
            url=self.url + commodities_endpoint, headers=self.PARAMS)

        CommoditiesreturnResult = pd.DataFrame.from_dict(
            ast.literal_eval(commodities_response.text))

        print("Available Commodities for Query: \n\n" +
              " | ".join(list(CommoditiesreturnResult.commodityName.unique())))

        self.commodityNameToId = CommoditiesreturnResult.set_index(
            "commodityName")[['commodityCode']].to_dict()['commodityCode']
        self.commodityIEdToName = CommoditiesreturnResult.set_index(
            "commodityCode")[['commodityName']].to_dict()['commodityName']

        CommoditiesreturnResult.to_csv("test.csv", index=False)

    def getCommodityId(self, commodity) -> np.int64:
        """

        Parameters
        ----------    
        commodity    : The commodity name based on the printed possible available inputs given above 

        Output
        ----------   
        Output       : int64, commodity id of the given commodity name

        Example Usage
        ----------   
        >>> commodity = CommodityItem(APIKEY)
        >>> commodity.getCommodityId('Corn')
        401 

        """

        return self.commodityNameToId[commodity]

    def getAvailableCountries(self) -> pd.DataFrame:
        r""" Returns a set of records with Countries and their corresponding Regions Codes the Country belongs to. 
        Use it to associate Country Name with Commodity Data records obtained by querying Commodity Data End point.

        Output
        ----------   
        Output       : Pandas Dataframe, containing the CountryCode, related CountryName, RegionID, 3 Letter Country Code and CountryDescription

        Example Usage
        ----------   
        >>> CommodityItem.getAvailableCountries().head(1)

        countryCode	 countryName	countryDescription	    regionId	gencCode
        1	          EUROPEAN	    EUROPEAN UNION - 27	        1	      null
        2	           UNKNOWN	         UNKNOWN	            99	       AX1
        1010	       GREENLD	        GREENLAND               11	       GRL
        1220	        CANADA	          CANADA                11	       CAN
        1610	        MIGUEL	   ST. PIERRE AND MIQUELON      11	      null
                                    ...  ...
        """

        countries_endpoint = "/api/esr/countries"

        countries_response = requests.get(
            url=self.url + countries_endpoint, headers=self.PARAMS).text

        return pd.DataFrame.from_dict(ast.literal_eval(countries_response.replace("null", '"null"')))

    def CountriesExportRecordsUSA(self, commodityCode: int, MarketYear: int = datetime.datetime.now().year) -> pd.DataFrame:
        r""" Given Commodity Code (Ex: 104 for Wheat - White ) and MarketYear (Ex: 2017) this API End point will return a list of US Export records of White Wheat to all applicable countries from USA for the given Market Year. 
        Please see DataReleaseDates end point to get a list of all Commodities and the corresponding Market Year data.
        || HIGHLIGHT: These numbers are export records of commodity to applicable countries **

        Data Release Frequency: Bi-Weekly

        Parameters
        ----------    
        commodityCode    : int64; commodity code
        MarketYear       : int64; year we want, 2019, 2020, 2021

        Output
        ----------   
        Output       : pandas dataframe; containing 'commodity', 'commodityCode', 'country', 'countryCode', 'weeklyExports', 'accumulatedExports','outstandingSales', 'grossNewSales', 'currentMYNetSales', 'currentMYTotalCommitment', 'nextMYOutstandingSales', 'nextMYNetSales', 'unitId', 'weekEndingDate'

        Example Usage
        ----------   
        >>> commodity = CommodityItem(APIKEY)
        >>> commodity.exportRecordsUSA(commodityCode = 401)

        commodity	commodityCode	country			countryCode		weeklyExports	accumulatedExports	outstandingSales	grossNewSales	currentMYNetSales	currentMYTotalCommitment	nextMYOutstandingSales	nextMYNetSales	unitId			date
            Corn		401			CANADA				1220			5599			5599				84173				36095			-7244					89772							0					0			1		2019-09-05
            Corn		401			MEXICO				2010			212010			212010				3407428				495420			193847					3619438							60000				0			1		2019-09-05
            Corn		401			GUATEMALA			2050			0				0					314990				20931			7564					314990							0					0			1		2019-09-05
            Corn		401			EL SALVADOR			2110			0				0					85254				15300			10235					85254							0					0			1		2019-09-05
            Corn		401			HONDURAS			2150			28435			28435				171196				54530			32274					199631							0					0			1		2019-09-05

                                                                                                ...		...		...		...		...		...	
        || NOTES: currentMYTotalCommitment - Signed Contracts for buying the commodity 
        """

        availableCountries = self.getAvailableCountries()
        mapCountries = availableCountries.set_index(
            "countryCode")[['countryDescription']].to_dict()['countryDescription']

        countriesExport_endpoint = f"/api/esr/exports/commodityCode/{commodityCode}/allCountries/marketYear/{MarketYear}"

        export_response = requests.get(
            url=self.url + countriesExport_endpoint, headers=self.PARAMS).text

        exportsdf = pd.DataFrame(ast.literal_eval(export_response))
        exportsdf['commodity'] = exportsdf.commodityCode.apply(
            lambda x: self.commodityIdToName[x])
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

    def CountryExportRecordsUSA(self, countryCode: int, commodityCode: int, MarketYear: int = datetime.datetime.now().year) -> pd.DataFrame:
        r"""Given Commodity Code (Ex: 104 for Wheat - White ), Country Code (Ex:1220 for Canada) and MarketYear (Ex: 2017) this API End point will return a list of US Export records of White Wheat to Canada from USA for the give Market Year. Please see DataReleaseDates end point to get a list of all Commodities and the corresponding Market Year data.

        || HIGHLIGHT: These numbers are export records of commodity to applicable countries **

        Data Release Frequency: Bi-Weekly

        Parameters
        ----------    
        commodityCode    : int64; commodity code
        countryCode      : int64; country code, see .getAvailableCountries()
        MarketYear       : int64; year we want, 2019, 2020, 2021

        """
        availableCountries = self.getAvailableCountries()
        mapCountries = availableCountries.set_index(
            "countryCode")[['countryDescription']].to_dict()['countryDescription']

        countryExport_endpoint = f"/api/esr/exports/commodityCode/{commodityCode}/countryCode/{countryCode}/marketYear/{MarketYear}"

        export_response = requests.get(
            url=self.url + countryExport_endpoint, headers=self.PARAMS).text

        exportsdf = pd.DataFrame(ast.literal_eval(export_response))
        exportsdf['commodity'] = exportsdf.commodityCode.apply(
            lambda x: self.commodityIdToName[x])
        exportsdf['country'] = mapCountries[countryCode]

        exportsdf.country = exportsdf.country.apply(
            lambda x: x.strip())  # Formatting dates and country spacing
        exportsdf['date'] = exportsdf.weekEndingDate.apply(
            lambda x: datetime.datetime.strptime(re.findall("....-..-..", x)[0], "%Y-%m-%d"))
        exportsdf = exportsdf.drop(columns=['weekEndingDate'])

        exportsdf = exportsdf[['date', 'commodity', 'commodityCode', 'country', 'countryCode', 'weeklyExports', 'accumulatedExports',
                               'outstandingSales', 'grossNewSales', 'currentMYNetSales', 'currentMYTotalCommitment', 'nextMYOutstandingSales', 'nextMYNetSales', 'unitId']]

        return exportsdf
