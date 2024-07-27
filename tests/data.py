import datetime

from app.schemas import Telemetry, Acknowledgement

telemetry = Telemetry(source="sensor_1",
                      timestamp="2024-07-24T12:00:00",
                      data={"temperature": 32.5, "humidity": 70})

broken_telemetry = Telemetry.model_construct(source=123,
                                             timestamp=datetime.datetime.strptime("2024-07-24 12:00:00", "%Y-%m-%d %H:%M:%S"),
                                             data=None)

ack = Acknowledgement(status="Success",
                      details={"message_id": "12345"})
