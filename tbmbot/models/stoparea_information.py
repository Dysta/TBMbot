from typing import List

from pydantic import BaseModel, Field


class Line(BaseModel):
    id: str
    name: str


class Route(BaseModel):
    id: str
    name: str
    line: Line


class StopPoint(BaseModel):
    id: str
    name: str
    routes: List[Route]
    has_wheelchair_boarding: bool = Field(..., alias="hasWheelchairBoarding")


class StopArea(BaseModel):
    id: str
    name: str
    city: str
    stop_points: List[StopPoint] = Field(..., alias="stopPoints")
