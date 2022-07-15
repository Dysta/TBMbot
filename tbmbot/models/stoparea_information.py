from typing import List, Tuple

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

    def extract_stop_id_and_line_id(self) -> List[Tuple[str, List[str]]]:
        """Return a list of Tuple containing the stop_id and the corresponding line_id"""
        res: List[Tuple[str, List[str]]] = []
        for s in self.stop_points:
            # ? stop_point:TBC:SP:XXXX | we get the XXXX
            stop_id = s.id.split(":")[-1]
            lines_id: list = []
            for r in s.routes:
                # ? line:TBC:XX | we get the XXXX
                line_id = r.line.id.split(":")[-1]
                line_name = r.line.name
                lines_id.append((line_name, line_id))

            res.append((stop_id, lines_id))

        return res
