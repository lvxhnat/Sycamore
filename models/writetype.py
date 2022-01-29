import os
from enum import Enum
from dotenv import load_dotenv
load_dotenv()


class DevStorageWriteType(str, Enum):
    localstorage = "localstorage"
    cloudstorage = "cloudstorage"
    databasestorage = "databasestorage"


class ProdStorageWriteType(str, Enum):
    cloudstorage = "cloudstorage"
    databasestorage = "databasestorage"


storage_type = DevStorageWriteType if os.environ['ENVIRONMENT'] == "dev" else ProdStorageWriteType
