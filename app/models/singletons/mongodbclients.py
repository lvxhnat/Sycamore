import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def main():

    main_client = MongoClient(
        os.getenv("MONGODB_CONNECTION_STRING"), tlsCAFile=certifi.where())
    visser_database = main_client['visser_main']
    visser_cache_database = main_client['visser_metadata']

    return visser_database, visser_cache_database


1

visser_database, visser_cache_database = main()

user_collection = visser_database['users']
historical_trading_metadata_collection = visser_cache_database['historical_trading_metadata']
user_call_metadata_collection = visser_cache_database['user_call_metadata']
twitter_metadata_collection = visser_cache_database['twitter_metadata']
