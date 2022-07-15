import itertools
from typing import List, Tuple

import disnake
from disnake import Member
from tbmbot.models import SearchItem
from tbmbot.utils import requester


class SearchInteraction:
    CANCEL_TEXT: str = "Annuler"
    CANCEL_EMOJI: str = "❌"
    mode_emoji: dict = {
        "Bus": "🚌",
        "stop_area": "🚏",
        "Tramway": "🚊",
        "Autocar": "🚍",
        "Ferry": "⛴",
    }


class _SearchDropdown(disnake.ui.Select):
    _banned: list = ["Autocar", "Ferry"]

    def __init__(self, opts: List[SearchItem]):
        o: list = [
            disnake.SelectOption(
                label=SearchInteraction.CANCEL_TEXT,
                description="Annuler la recherche actuelle.",
                emoji=SearchInteraction.CANCEL_EMOJI,
                value=SearchInteraction.CANCEL_TEXT,
            )
        ]
        for e in itertools.islice(opts, 0, 24):
            # if e.mode in _SearchDropdown._banned:
            #     continue
            desc: str = f"{e.city} ({e.insee})" if e.city and e.insee else ""
            value: str = e.url.replace(requester.BASE_PATH, "")
            o.append(
                disnake.SelectOption(
                    label=e.name,
                    description=desc,
                    emoji=SearchInteraction.mode_emoji.get(e.mode, "⁉"),
                    value=f"{e.type}|{value}",
                )
            )

        super().__init__(
            placeholder="Choisissez un résultat", min_values=1, max_values=1, options=o
        )


class SearchView(disnake.ui.View):
    def __init__(self, author: Member, opts: List[SearchItem]):
        super().__init__(timeout=15.0)
        self._timeout = False
        self._author = author
        self._drop = _SearchDropdown(opts)
        self.add_item(self._drop)
        self._message = None

    async def interaction_check(self, inter: disnake.Interaction) -> bool:
        if inter.user != self._author:
            return False

        self._drop.disabled = True
        await inter.response.edit_message(view=self)
        self.stop()

    async def on_timeout(self) -> None:
        self._timeout = True
        self._drop.disabled = True
        await self._message.edit(view=self)

    @property
    def result(self) -> (str, str):
        if self._timeout:
            return "", SearchInteraction.CANCEL_TEXT
        return tuple(self._drop.values[0].split("|"))

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, msg):
        self._message = msg
