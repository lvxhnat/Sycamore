import uuid
from app.models.metadata import HistoricalTradingMetadataInterface
from app.models.singletons.mongodbclients import historical_trading_metadata_collection
from app.models.endpoints.trading import DefaultTradingParamsBaseModel
from app.utils.storage.storage_urls import trading_metadata_storage_url


def historical_trading_metadata_middleware(
        job_params: DefaultTradingParamsBaseModel) -> bool:

    try:
        historical_trading_metadata: HistoricalTradingMetadataInterface = {
            "_id": str(uuid.uuid4()),
            "ticker": job_params['ticker'],
            "from_date": job_params['from_date'],
            "to_date": job_params['to_date'],
            "resolution": job_params['resolution'],
            "instrument": job_params['instrument'],
            "write_path": trading_metadata_storage_url(job_params)
        }
        historical_trading_metadata_collection.insert_one(
            historical_trading_metadata)

        return True

    except Exception as e:
        return False
