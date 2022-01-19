from pydantic import BaseModel, Field
from typing import List


class DefaultTwitterBaseModel(BaseModel):
    user_ids: List[int or str] = Field(
        None, description="List of user id strings or integers in format: [...] or [..., ..., ...]")
    screen_names: List[str] = Field(
        None, description="List of user id strings or integers in format: [...] or [..., ..., ...]")

    class Config:
        schema_extra = {
            "example": {
                "user_ids": ["320524842", "985839765693059072", "1323090848", "173149432", "36724495"],
                "screen_names": None
            }
        }


class FollowersBaseModel(DefaultTwitterBaseModel):
    pass


class FollowingsBaseModel(DefaultTwitterBaseModel):
    pass
