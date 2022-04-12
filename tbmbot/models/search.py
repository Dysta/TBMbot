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


class Search(BaseModel):
    __root__: List[SearchItem]
