import os
from enum import Enum
from dotenv import load_dotenv
load_dotenv()


class DevStorageWriteType(str, Enum):
    returnitem = "return"
    localstorage = "localstorage"
    cloudstorage = "cloudstorage"
    databasestorage = "databasestorage"


class ProdStorageWriteType(str, Enum):
    returnitem = "return"
    cloudstorage = "cloudstorage"
    databasestorage = "databasestorage"


storage_type = DevStorageWriteType if os.environ['ENVIRONMENT'] == "dev" else ProdStorageWriteType
