from typing import List

from pydantic import BaseModel, Field


class Alert(BaseModel):
    title: str
    working_network: bool = Field(..., alias="workingNetwork")
    description: str
    cause_name: str = Field(..., alias="causeName")


class Impact(BaseModel):
    alert: Alert


class AlertItem(BaseModel):
    id: str
    name: str
    impacts: List[Impact]
    transport_mode: int = Field(..., alias="transportMode")


class Alerts(BaseModel):
    __root__: List[AlertItem]
