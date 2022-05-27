import pandas as pd
from typing_extensions import TypedDict


class NASSCropProductionInfo(TypedDict):
    frequency: str
    upcoming_dates: list
    df: pd.DataFrame
