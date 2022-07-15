from typing import List, Optional, Tuple

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
    stop_points: List[StopPoint] = Field(..., alias="stopPoints")
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

    def get_external_code_for_stop_point(
        self, stop_point: str
    ) -> Tuple[Optional[str], Optional[str]]:
        ret = [None, None]
        for i, r in enumerate(self.routes):
            for s in r.stop_points:
                if s.name.lower() == stop_point.lower():
                    ret[i] = s.external_code

        return tuple(ret)
