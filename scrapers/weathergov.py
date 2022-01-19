import re
import requests
import numpy as np
import pandas as pd
from datetime import datetime

from sycamore.alerts.logger import logger
from sycamore.scrapers.base import BaseClient


class WeatherGovScraperClient(BaseClient):

    def __init__(self):
        super().__init__(self)

    def get_weather_gov_station_data(self, station_id: str):
        ''' Get List of Weather Metadata from the Weather Gov API for the past 7 days, for a particular station indicated in station_id

        Parameters
        =============
        station_id -> [str]: Station ID String, need to source out list of stations available 

        Outputs
        =============
        pd.DataFrame containing JSON metadata

        Example Usage 
        =============
        >>> get_weather_gov_station_data("KBTV")
            observation_item	coordinates	station	timestamp	weather_description	temperature	temperature_units	dewpoint	dewpoint_units	wind_direction	...	precipitation_last_6hours_units	relative_humidity	relative_humidity_units	wind_chill	wind_chill_units	heat_index	heat_index_units	cloud_layers	cloud_layers_units	cloud_layers_amount
        0	https://api.weather.gov/stations/KBTV/observat...	[-73.15, 44.47]	https://api.weather.gov/stations/KBTV	2022-01-01 11:54:00	Cloudy	3.3	wmoUnit:degC	1.7	wmoUnit:degC	170.0	...	wmoUnit:m	89.254284	wmoUnit:percent	0.386307	wmoUnit:degC	None	wmoUnit:degC	940	wmoUnit:m	OVC
        1	https://api.weather.gov/stations/KBTV/observat...	[-73.15, 44.47]	https://api.weather.gov/stations/KBTV	2022-01-03 04:54:00	Partly Cloudy	-10.0	wmoUnit:degC	-14.4	wmoUnit:degC	30.0	...	wmoUnit:m	70.206165	wmoUnit:percent	-15.630509	wmoUnit:degC	None	wmoUnit:degC	730	wmoUnit:m	SCT
        .
        .
        .

        '''

        stations = requests.get(
            f"https://api.weather.gov/stations/{station_id}/observations").text

        df = eval(stations.replace("null", "''"))['features']

        dataframe = pd.DataFrame(
            list(map(lambda x: self.process_weather_json_to_dict(x), df)))
        dataframe.timestamp = dataframe.timestamp.apply(
            lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S+00:00"))

        return dataframe

    def try_key_value(self, item: dict, key: list):
        ''' Tries to unnest and get value of dictionary key. 

        Parameters
        =============
        item -> [dict]: target dictionary to unnest values
        key -> [list]: list of keys to unnest, with the parent key at the first index position 

        Outputs
        =============
        [dict_value] : the value, according to the type that was in the unnested value
        '''
        try:
            parent_key = key[0]
            value = item[parent_key]
            for key_item in key[1:]:
                value = value[key_item]
            return value if value != "" else None
        except:
            return None

    def process_weather_json_to_dict(self, json_item):
        data = {}
        data['observation_item'] = self.try_key_value(json_item, ['id'])
        data['coordinates'] = str(self.try_key_value(
            json_item, ['geometry', 'coordinates']))
        data['station'] = self.try_key_value(
            json_item, ['properties', 'station'])
        data['timestamp'] = self.try_key_value(
            json_item, ['properties', 'timestamp'])
        data['weather_description'] = self.try_key_value(
            json_item, ['properties', 'textDescription'])

        # The actual key value in the json item
        property_values = ['temperature', 'dewpoint', 'windDirection', 'windSpeed', 'windGust', 'barometricPressure', 'seaLevelPressure', 'visibility', 'maxTemperatureLast24Hours',
                           'minTemperatureLast24Hours', 'precipitationLastHour', 'precipitationLast3Hours', 'precipitationLast6Hours', 'relativeHumidity', 'windChill', 'heatIndex']
        # The name we want to map it to
        property_names = ['temperature', 'dewpoint', 'wind_direction', 'wind_speed', 'wind_gust', 'barometric_pressure', 'sea_level_pressure', 'visibility', 'max_temp_p24h',
                          'min_temp_p24h', 'precipitation_last_hour', 'precipitation_last_3hours', 'precipitation_last_6hours', 'relative_humidity', 'wind_chill', 'heat_index']

        for values, names in zip(property_values, property_names):
            data[names] = self.try_key_value(
                json_item, ['properties', values, 'value'])
            data[names + "_units"] = self.try_key_value(
                json_item, ['properties', values, 'unitCode'])

        try:
            data['cloud_layers'] = self.try_key_value(
                json_item, ['properties', 'cloudLayers'])[0]['base']['value']
        except:
            data['cloud_layers'] = None
        try:
            data['cloud_layers_units'] = self.try_key_value(
                json_item, ['properties', 'cloudLayers'])[0]['base']['unitCode']
        except:
            data['cloud_layers_units'] = None
        try:
            data['cloud_layers_amount'] = self.try_key_value(
                json_item, ['properties', 'cloudLayers'])[0]['amount']
        except:
            data['cloud_layers_amount'] = None

        return data
