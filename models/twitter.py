from pydantic import BaseModel, Field
from typing import List


class DefaultTwitterParamsBaseModel(BaseModel):
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


class DefaultTwitterResponseBaseModel(BaseModel):
    job_id: str
    write_type: str
    write_path: str
    users_requested_extracted: int
    users_requested: int
    time_elapsed_seconds: int

    class Config:
        schema_extra = {
            "example": {
                "job_id": '12c6f2a1-8022-4965-b5fe-e210b7e4deba',
                "write_type": 'localstorage',
                "users_requested": 3210,
                "users_requested_extracted": 3201,
                "time_elapsed_seconds": 43411,
                "write_path": 'gs://some-bucket/data/twitter/followers/0003_202103120505/'
            }
        }


class FollowersResponse(DefaultTwitterResponseBaseModel):
    pass


class FollowingsResponse(DefaultTwitterResponseBaseModel):
    pass


class FollowersParams(DefaultTwitterParamsBaseModel):
    pass


class FollowingsParams(DefaultTwitterParamsBaseModel):
    pass
