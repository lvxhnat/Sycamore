from models.singletons.mongodbclients import usertransaction_collection
from functools import wraps
import sys

sys.path.append("..")


def store_mongodb_metadata(func):
    @wraps(func)
    def foo(*args, **kwargs):
        meta_data = func(*args, **kwargs)
        usertransaction_collection.insert_one(meta_data)
        return meta_data
    return foo
