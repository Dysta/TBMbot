import disnake
from disnake.ext import commands
from loguru import logger
from tbmbot.models import Alerts, LineInformation
from tbmbot.models import Search as Search_m
from tbmbot.utils import embeds, requester

from . import Information


class Search(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    async def _callback(self, inter: disnake.Interaction, opts: str):
        embed_to_send: list = []
        logger.debug(f"Get info for line {opts}")

        status, content = await requester.get_line_info(opts)
        if status != 200:
            logger.error(
                f"Unable to get any information for '{opts}'. Status returned: {status}."
            )
            await inter.response.send_message(
                "❌ | Oops.. Quelque chose s'est mal passé..", ephemeral=True
            )
            return

        line_data: LineInformation = LineInformation.parse_raw(content)
        e: disnake.Embed = embeds.line_info_embed(line_data)
        embed_to_send.append(e)

        status, content = await requester.get_line_alerts(opts)
        if status == 200:
            alerts_data: Alerts = Alerts.parse_raw(content)
            ae: disnake.Embed = embeds.line_perturbation_embed(alerts_data)
            embed_to_send.append(ae)
        else:
            logger.info(f"No perturbation found for '{opts}'")

        await inter.response.send_message(embeds=embed_to_send)

    @commands.slash_command(
        description="Rechercher un tram, un bus ou un arrêt. 🔎",
    )
    async def search(
        self,
        inter: disnake.CommandInteraction,
        recherche: str,
    ):
        await inter.response.defer(with_message=True)

        status, content = await requester.search_for(recherche)
        logger.debug(status)
        logger.debug(content)
        if status != 200 or content == "":
            await inter.send(
                f":x: | Rien trouvé pour `{recherche}`.", delete_after=10.0
            )
            return

        try:
            search_result: Search_m = Search_m.parse_raw(content)
        except Exception as e:
            logger.error(e)

        tpe, id = search_result.get_type_and_id_for(recherche)

        logger.debug(id)
        logger.debug(tpe)

        if tpe != "stop_area":
            try:
                await Information._line_callback(inter, line_id=id)
                return
            except Exception as e:
                logger.error(e)

            return
        elif tpe == "stop_area":
            try:
                await Information._stop_callback(inter, stop_id=id)
                return
            except Exception as e:
                logger.error(e)
        else:
            logger.error(f"Unsupported id '{id}' for type {tpe}.")
            await inter.response.send_message(
                "❌ | Oops.. Quelque chose s'est mal passé..", ephemeral=True
            )
            return

    @search.autocomplete("recherche")
    async def search_autocomplete(self, inter: disnake.CommandInteraction, string: str):
        status, content = await requester.search_for(string)
        if status != 200 or content == "":
            return []

        logger.debug(status)
        logger.debug(content)
        try:
            search_result: Search_m = Search_m.parse_raw(content)
            return [s.name for s in search_result.__root__][:20]
        except Exception as e:
            logger.error(e)
            return []


def setup(bot):
    bot.add_cog(Search(bot))
