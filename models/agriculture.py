from pydantic import BaseModel, Field
from typing import Dict


class DefaultAgriculturalBaseModel(BaseModel):

    class Config:
        pass

class AgriculturalResponse(BaseModel):
    pass