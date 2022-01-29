from pydantic import BaseModel, Field
from typing import Dict


class DefaultBaseModel(BaseModel):
    user: str
    job_id: str
    write_type: str
    write_path: str
    date_extracted: str
    job_description: Dict[str, str]
    time_elapsed_seconds: int
