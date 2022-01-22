import pandas as pd
from pydantic import BaseModel


class AgriculturalOutput(BaseModel):
    output: int
