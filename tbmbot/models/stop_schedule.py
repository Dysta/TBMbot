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
    line_name: str  # injected in requester.get_stop_schedule


class Schedule(BaseModel):
    __root__: List[ScheduleItem]
