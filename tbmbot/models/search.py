from typing import List, Optional

from pydantic import BaseModel


class SearchItem(BaseModel):
    id: str
    name: str
    type: str
    mode: str
    url: str
    city: Optional[str] = None
    insee: Optional[str] = None

    @property
    def is_stop(self) -> bool:
        return self.type == "stop_area"


class Search(BaseModel):
    __root__: List[SearchItem]
