from datetime import datetime

from app.models.base import DefaultBaseModel


class DefaultAgriculturalResponseBaseModel(DefaultBaseModel):

    class Config:
        schema_extra = {
            "example": {
                "user": "james201",
                "date_extracted": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "job_id": '12c6f2a1-8022-4965-b5fe-e210b7e4deba',
                "write_type": 'localstorage',
                "job_description": {},
                "time_elapsed_seconds": 43411,
                "write_path": 'gs://some-bucket/data/agriculture/ethanolprod/0003_202103120505/'
            }
        }


class AgriculturalResponse(DefaultAgriculturalResponseBaseModel):
    pass
