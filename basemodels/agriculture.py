from pydantic import BaseModel, Field
from typing import Dict


class DefaultAgriculturalBaseModel(BaseModel):
    agricultural_mapping: Dict[str, str]

    class Config:
        pass
