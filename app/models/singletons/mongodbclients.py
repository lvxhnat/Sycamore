import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

from app.utils.alerts.logger import logger
load_dotenv()


def main():

    main_client = MongoClient(
        os.getenv("MONGODB_CONNECTION_STRING"), tlsCAFile=certifi.where())
    visser_database = main_client['Visser']
    sycamore_database = main_client['Sycamore']

    return sycamore_database, visser_database


sycamore_database, visser_database = main()

user_collection = visser_database['users']
usertransaction_collection = sycamore_database['user_transactions']

logger.info("Database singleton instantiated")
