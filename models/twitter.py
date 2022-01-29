import os
from dotenv import load_dotenv
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from models import writetypes
load_dotenv()


class DefaultTwitterParamsBaseModel(BaseModel):
    user_ids: List[int or str] = Field(
        None, description="List of user id strings or integers in format: [...] or [..., ..., ...]")
    screen_names: List[str] = Field(
        None, description="List of user id strings or integers in format: [...] or [..., ..., ...]")
    write_type: Optional[writetypes.StorageWriteType] = os.environ['DEFAULT_WRITE_TYPE']

    class Config:
        schema_extra = {
            "example": {
                "user_ids": ["320524842", "985839765693059072", "1323090848", "173149432", "36724495"],
                "screen_names": None
            }
        }


class DefaultTwitterResponseBaseModel(BaseModel):
    user: str
    job_id: str
    write_type: str
    write_path: str
    date_extracted: str
    job_description: Dict[str, str]
    time_elapsed_seconds: int

    class Config:
        schema_extra = {
            "example": {
                "user": "james201",
                "date_extracted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "job_id": '12c6f2a1-8022-4965-b5fe-e210b7e4deba',
                "write_type": 'localstorage',
                "job_description": {
                    "users_requested": 3210,
                    "users_requested_extracted": 3201,
                },
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
