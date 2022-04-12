from typing import List, Optional

from pydantic import BaseModel, Field


class StopPoint(BaseModel):
    id: str
    name: str
    full_label: str = Field(..., alias="fullLabel")
    external_code: str = Field(..., alias="externalCode")
    city: str


class Route(BaseModel):
    id: str
    name: str
    start: str
    end: str
    # stop_points: List[StopPoint] = Field(..., alias="stopPoints")
    external_code: str = Field(..., alias="externalCode")


class LineSchedule(BaseModel):
    begin: str
    end: str
    frequency: Optional[str]
    navigation_amplitude: Optional[str] = Field(..., alias="navigationAmplitude")


class LineMap(BaseModel):
    thermometer_image: str = Field(..., alias="thermometerImage")


class Terminus(BaseModel):
    route: str
    stop_points: List[StopPoint] = Field(..., alias="stopPoints")


class LineInformation(BaseModel):
    id: str
    name: str
    code: str
    type: str
    color: str
    external_code: str = Field(..., alias="externalCode")
    routes: List[Route]
    line_maps: List[LineMap] = Field(..., alias="lineMaps")
    terminus: List[Terminus]
    line_schedules: List[LineSchedule] = Field(..., alias="lineSchedules")
