import os
import certifi
from dotenv import load_dotenv
from pymongo import MongoClient

from utils.alerts.logger import logger
load_dotenv()


def main():

    main_client = MongoClient('mongodb+srv://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] +
                              '@' + os.environ['MONGODB_CLUSTERNAME'] + '.nsb6k.mongodb.net/myFirstDatabase?retryWrites=true&w=majority', tlsCAFile=certifi.where())
    visser_database = main_client['Visser']
    sycamore_database = main_client['Sycamore']

    return sycamore_database, visser_database


sycamore_database, visser_database = main()

user_collection = visser_database['users']
usertransaction_collection = sycamore_database['user_transactions']

logger.info("Database singleton instantiated")
