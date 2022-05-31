from pydantic import BaseModel
from typing import Dict, Literal

AllowedWriteTypes = Literal['return',
                            'localstorage', 'cloudstorage', 'databasestorage']

class DefaultBaseModel(BaseModel):
    user: str
    job_id: str
    end_point: str
    write_type: AllowedWriteTypes
    write_path: str
    date_extracted: str
    job_description: Dict[str, str]
    time_elapsed_seconds: int
