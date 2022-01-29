import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient

from alerts.logger import logger
load_dotenv()
sys.path.append("...")

logger.info("Database initialised")
main_client = MongoClient('mongodb+srv://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] +
                          '@' + os.environ['MONGODB_CLUSTERNAME'] + '.nsb6k.mongodb.net/myFirstDatabase?retryWrites=true&w=majority')
visser_database = main_client['Visser']
sycamore_database = main_client['Sycamore']

user_collection = visser_database['users']
usertransaction_collection = sycamore_database['user_transactions']
