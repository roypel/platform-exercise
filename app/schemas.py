from datetime import datetime
from typing import Dict, Any

from pydantic import BaseModel, Field


class Telemetry(BaseModel):
    source: str = Field(..., description="The identifier of the source")
    timestamp: datetime = Field(..., description="The timestamp when the telemetry data was sent")
    data: Dict = Field(..., description="The actual telemetry data")

    class Config:
        schema_extra = {
            "example": {
                "source": "sensor_1",
                "timestamp": "2024-07-24T12:00:00Z",
                "data": {"temperature": 32.5, "humidity": 70}
            }
        }


class Acknowledgement(BaseModel):
    status: str = Field(..., description="The status of the acknowledgement, e.g. 'Success', 'DB error'")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details about the acknowledgement")

    class Config:
        schema_extra = {
            "example": {
                "status": "Success",
                "details": {"message_id": "12345"}
            }
        }


class DBError(Exception):
    pass
