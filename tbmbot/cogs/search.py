import itertools

from . import Information, __TESTING_GUILDS_ID__

import nextcord

from loguru import logger
from nextcord.ext import commands

from tbmbot.models import LineInformation, Alerts, StopArea
from tbmbot.models import Search as Search_m
from tbmbot.utils import embeds, requester
from ..views import SearchView, SearchInteraction


class Search(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    async def _callback(self, inter: nextcord.Interaction, opts: str):
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
        e: nextcord.Embed = embeds.line_info_embed(line_data)
        embed_to_send.append(e)

        status, content = await requester.get_line_alerts(opts)
        if status == 200:
            alerts_data: Alerts = Alerts.parse_raw(content)
            ae: nextcord.Embed = embeds.line_perturbation_embed(alerts_data)
            embed_to_send.append(ae)
        else:
            logger.info(f"No perturbation found for '{opts}'")

        await inter.response.send_message(embeds=embed_to_send)

    @nextcord.slash_command(
        guild_ids=__TESTING_GUILDS_ID__,
        description="Rechercher un tram, un bus ou un arrêt. 🔎",
    )
    async def search(
        self,
        inter: nextcord.Interaction,
        opts: str = nextcord.SlashOption(
            name="recherche",
            description="Nom de la ligne ou de l'arrêt",
            required=True,
        ),
    ):
        await inter.response.defer(with_message=True)

        status, content = await requester.search_for(opts)
        if status != 200 or content == "":
            await inter.send(f"Rien trouvé pour `{opts}`.", ephemeral=True)
            return

        logger.debug(status)
        logger.debug(content)
        try:
            search_result: Search_m = Search_m.parse_raw(content)
        except Exception as e:
            logger.error(e)
        view: SearchView = SearchView(inter.user, search_result.__root__)
        logger.debug(search_result)
        try:
            await inter.send(view=view)
            view.message = await inter.original_message()
        except Exception as e:
            logger.error(e)
            return

        timeout = await view.wait()
        if timeout:
            return
        tpe, url = view.result
        if url == SearchInteraction.CANCEL_TEXT:
            return

        logger.debug(url)
        logger.debug(tpe)

        if tpe != "stop_area":
            try:
                opts: str = url.split("/")[-1]
                await Information._callback(inter, opts)
                return
            except Exception as e:
                logger.error(e)

            return

        status, content = await requester.get(url)
        if status != 200 or content == "":
            await inter.edit_original_message(content=f"Rien trouvé pour `{opts}`.")
            return

        try:
            data: StopArea = StopArea.parse_raw(content)
        except Exception as e:
            logger.error(e)

        e: nextcord.Embed = nextcord.Embed(
            title=f"{data.name} ({data.city})",
            description="",
            colour=nextcord.Colour.darker_grey(),
        )
        #  we short stop points by name
        s_sp = sorted(data.stop_points, key=lambda x: x.name)
        #  then we group it
        g_sp = itertools.groupby(s_sp, key=lambda x: x.name)

        for name, stops in g_sp:
            #  we add all the routes together
            rts = itertools.chain(*[s.routes for s in stops])
            s_rts = sorted(rts, key=lambda x: x.line.name)
            logger.debug(s_rts)
            val = "\n".join([f"`{r.line.name: <10}` ➡ **{r.name}**" for r in s_rts])
            e.add_field(name=f"🚏 | {name}", value=val, inline=False)

        await inter.edit_original_message(embed=e, view=None)


def setup(bot):
    bot.add_cog(Search(bot))
