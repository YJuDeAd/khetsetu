from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str

    model_config = ConfigDict(from_attributes=True)
