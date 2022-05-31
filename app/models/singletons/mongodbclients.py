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
    sycamore_database = main_client['Sycamore']

    return sycamore_database, visser_database, visser_cache_database


sycamore_database, visser_database, visser_cache_database = main()

user_collection = visser_database['users']
usertransaction_collection = sycamore_database['user_transactions']
