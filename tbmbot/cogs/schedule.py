from typing import Callable, List

import disnake
from disnake.ext import commands
from loguru import logger
from tbmbot.models import Schedule as Schedule_m
from tbmbot.models import Search, SearchItem, StopArea
from tbmbot.utils import embeds, requester


class Schedule(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    async def _autocomplet_meta(
        self, query: str, predicat: Callable[[SearchItem], bool]
    ) -> List[str]:
        status, content = await requester.search_for(query)
        if status != 200 or content == "":
            return []

        logger.debug(status)
        logger.debug(content)
        try:
            search_result: Search = Search.parse_raw(content)
            return [
                f"{s.name} — {s.city}" for s in search_result.__root__ if predicat(s)
            ][:20]
        except Exception as e:
            logger.error(e)
            return []

    @commands.slash_command(
        description="Récupérer les horaires pour un arrêt ⏰",
    )
    async def horaire(
        self,
        inter: disnake.CommandInteraction,
        arret: str,
    ):
        await inter.response.defer(with_message=True)

        logger.debug(arret)

        if "—" in arret:
            arret, city = arret.split("—")
            arret = arret.strip()
            city = city.strip()
            logger.debug(arret)
            logger.debug(city)

        status, content = await requester.search_for(arret)
        logger.debug(status)
        logger.debug(content)
        if status != 200 or content == "":
            await inter.send(f":x: | Rien trouvé pour {arret}.", delete_after=10.0)
            return

        try:
            search_result: Search = Search.parse_raw(content)
        except Exception as e:
            logger.error(e)
            return

        stop_item = search_result.get_item_for(arret, city)
        if not stop_item:
            await inter.send(
                f":x: | Rien trouvé pour {arret} — {city}.", delete_after=10.0
            )
            return

        stop_id = stop_item.id
        stop_name = stop_item.name
        stop_city = stop_item.city

        logger.debug(stop_id)
        logger.debug(stop_name)

        status, content = await requester.get_stop_info(stop_id)
        if status != 200 or content == "":
            await inter.response.send_message(content=f"Rien trouvé pour `{arret}`.")
            return

        try:
            stop_data: StopArea = StopArea.parse_raw(content)
        except Exception as e:
            logger.error(e)
            await inter.response.send_message(
                "❌ | Oops.. Quelque chose s'est mal passé..", ephemeral=True
            )
            return

        logger.debug(stop_data)

        stop_line_ids = stop_data.extract_stop_id_and_line_id()
        logger.debug(stop_line_ids)

        schedule_list: list = []

        for s_id, l_ids in stop_line_ids:
            for l_name, l_id in l_ids:
                status, content = await requester.get_stop_schedule(s_id, l_id)
                if status != 200 or content == "":
                    continue
                try:
                    schedule_data: Schedule_m = Schedule_m.parse_raw(content)
                    logger.debug(schedule_data)
                    for s in schedule_data.__root__:
                        s.line_name = l_name
                        s.line_id = int(l_id)
                    schedule_list.append(schedule_data)
                except Exception as e:
                    logger.error(f"Error during parsing of schedules: {e}")
                    logger.error(
                        f"Data used: stop_id {s_id}, line_id {l_id}, line_name {l_name}"
                    )

        # ? we short by line_name
        # ? we just need to take the first bc all the others in the root have the same name
        schedule_list = sorted(schedule_list, key=lambda x: x.__root__[0].line_name)

        e: disnake.Embed = embeds.line_schedule_embed(
            f"⌚ {stop_name} — {stop_city}", schedule_list
        )
        await inter.edit_original_message(embed=e)

    @horaire.autocomplete("arret")
    async def arret_autocomplet(self, inter: disnake.CommandInteraction, string: str):
        return await self._autocomplet_meta(string, lambda x: x.type == "stop_area")


def setup(bot):
    bot.add_cog(Schedule(bot))
