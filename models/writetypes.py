from enum import Enum


class StorageWriteType(str, Enum):
    localstorage = "localstorage"
    cloudstorage = "cloudstorage"
    databasestorage = "databasestorage"
