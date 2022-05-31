import uuid
from typing import Literal
from datetime import datetime

from app.models.trading import SupportedTradingEndpoints
from app.models.base import AllowedWriteTypes

allowed_endpoints = Literal[
    SupportedTradingEndpoints,
]


def generate_base_metadata(
    endpoint: allowed_endpoints,
    user: str,
    write_type: AllowedWriteTypes,
    write_path: str,
):
    return {
        "user": user,
        "end_point": '/'.join(endpoint.split("_")),
        "date_extracted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "job_id": str(uuid.uuid4()),
        "write_type": write_type,
        "write_path": write_path,
    }
