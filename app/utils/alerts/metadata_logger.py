import uuid
from datetime import datetime

from app.models.singletons.mongodbclients import usertransaction_collection


def log_metadata(user: str, endpoint: str, write_type: str, job_description: dict, time_elapsed_seconds: int, write_path: str):
    meta_data = {
        "user": user,
        "end_point": '/'.join(endpoint.split("_")),
        "date_extracted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "job_id": str(uuid.uuid4()),
        "write_type": write_type,
        "job_description": job_description,
        "time_elapsed_seconds": time_elapsed_seconds,
        "write_path": write_path,
    }
    usertransaction_collection.insert_one(meta_data)
    return meta_data
