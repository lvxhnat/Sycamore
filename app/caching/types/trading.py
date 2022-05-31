from pyclbr import Function
from app.models.trading import SupportedTradingResolutions, SupportAssetTypes
from app.models.base import AllowedWriteTypes
from app.caching.types.base import generate_base_metadata
from app.caching.types.models.trading import HistoricalDataModel
from app.models.trading import SupportedTradingEndpoints


def generate_trading_metadata_creator(
    endpoint: SupportedTradingEndpoints
) -> Function:
    function_mapping = {
        "historical": generate_historical_metadata
    }

    return function_mapping[endpoint]


def generate_historical_metadata(
    user: str,
    write_type: AllowedWriteTypes,
    write_path: str,
    ticker: str,
    from_date: str,
    to_date: str,
    resolution: SupportedTradingResolutions,
    instruments: SupportAssetTypes,
) -> HistoricalDataModel:
    ''' Generate the metadata required to populate our database for historical data endpoint.
    '''

    endpoint = "historical"
    base_metadata = generate_base_metadata(
        endpoint=endpoint,
        user=user,
        write_type=write_type,
        write_path=write_path,
    )
    for key, value in zip(['ticker', 'from_date', 'to_date', 'resolution', 'instruments'], [ticker, from_date, to_date, resolution, instruments]):
        base_metadata[key] = value

    return base_metadata
