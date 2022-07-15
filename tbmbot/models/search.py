from typing import List, Optional, Tuple

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

    def get_item_for(self, query: str) -> Optional[SearchItem]:
        for e in self.__root__:
            if e.name.lower() == query.lower():
                return e
        return None

    def get_type_and_id_for(self, query: str) -> Optional[Tuple[str, str]]:
        for e in self.__root__:
            if e.name.lower() == query.lower():
                return e.type, e.id
        return None

    def get_name(self, query: str) -> Optional[str]:
        for e in self.__root__:
            if e.name.lower() == query.lower():
                return e.name
        return None
