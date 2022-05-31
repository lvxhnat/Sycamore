from __future__ import annotations
from typing import Literal, Optional, Dict

from datetime import datetime

from app.models.singletons.mongodbclients import visser_cache_database
from app.models.trading import DefaultTradingParamsBaseModel, SupportedTradingEndpoints
from app.utils.alerts.logger import logging
from app.caching.types.trading import generate_trading_metadata_creator


def instantiate_user_session(user: str) -> bool:
    ''' Instantiates the user as a session in the metadata database
    Parameters 
    -------------
    user    : The username of the user 
    '''
    try:
        timestamp = datetime.today()
        visser_cache_database['user_sessions'].insert_one({
            "user": user,
            "session_start": timestamp,
            "session_last_call": None,
            "queries": 0,
        })
        return True
    except Exception as e:
        return False


def user_session_ping(user: str, timestamp: datetime):
    ''' Updates the user for a single api call
     Parameters 
    -------------
    user    : The username of the user 
    '''
    try:
        visser_cache_database['user_sessions'].update_one({
            "user": user
        }, {{
            "$set": {
                "user": user,
                "session_last_call": timestamp
            }
        }, {
            "$inc": {
                "queries": 1
            }}
        })
        return True

    except:
        return False


def record_trading_metadata(
    user: str,
    write_type: str,
    write_path: Optional[str],
    job_params: DefaultTradingParamsBaseModel | None,
    job_metadata: Dict[str, str],
    endpoint: SupportedTradingEndpoints,
):

    try:
        # visser_cache_database['trading_metadata'].insert_one({})
        return True

    except Exception as e:
        logging.error(e)
        return False
