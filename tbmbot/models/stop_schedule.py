from __future__ import annotations

import json
from typing import List, Optional, Type

from loguru import logger
from pydantic import BaseModel, Protocol, StrBytes


class ScheduleItem(BaseModel):
    waittime_text: str
    destination_name: str
    departure: str
    waittime: str
    updated_at: str
    line_name: Optional[str]
    line_id: Optional[int]


class Schedule(BaseModel):
    __root__: List[ScheduleItem]

    @classmethod
    def parse_raw(
        cls: Type["Model"],
        b: StrBytes,
        *,
        content_type: str = None,
        encoding: str = "utf8",
        proto: Protocol = None,
        allow_pickle: bool = False,
    ) -> "Model":
        # ? we convert current json to dict to easily remove the unknown 'destination_key'
        data: dict = json.loads(b)

        # ? we remove the 'destination' key
        data = data.pop("destinations")

        # ? since the 'destination_id' key isn't know, we just extract the content
        schedules: list = list(data.values())[0]

        # ? then we build our custom Schedule class
        return super().parse_raw(
            json.dumps(schedules),
            content_type=content_type,
            encoding=encoding,
            proto=proto,
            allow_pickle=allow_pickle,
        )
