import itertools

import disnake

from loguru import logger
from disnake.ext import commands

from tbmbot.models import LineInformation, Alerts, Search, StopArea
from tbmbot.utils import embeds, requester


class Information(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @staticmethod
    async def _line_callback(inter: disnake.Interaction, line_id: str):
        embed_to_send: list = []
        logger.debug(f"Get info for line {line_id}")

        status, content = await requester.get_line_info(line_id)
        if status != 200:
            logger.error(
                f"Unable to get any information for '{line_id}'. Status returned: {status}."
            )
            await inter.response.send_message(
                "❌ | Oops.. Quelque chose s'est mal passé..", ephemeral=True
            )
            return

        line_data: LineInformation = LineInformation.parse_raw(content)
        e: disnake.Embed = embeds.line_info_embed(line_data)
        embed_to_send.append(e)

        status, content = await requester.get_line_alerts(line_id)
        if status == 200:
            alerts_data: Alerts = Alerts.parse_raw(content)
            ae: disnake.Embed = embeds.line_perturbation_embed(alerts_data)
            embed_to_send.append(ae)
        else:
            logger.info(f"No perturbation found for '{line_id}'")

        if inter.response.is_done():
            await inter.edit_original_message(embeds=embed_to_send)
        else:
            await inter.response.send_message(embeds=embed_to_send)

    @staticmethod
    async def _stop_callback(inter: disnake.Interaction, stop_id: str):
        logger.debug(f"Get info for stop {stop_id}")

        status, content = await requester.get_stop_info(stop_id)
        if status != 200 or content == "":
            await inter.response.send_message(content=f"Rien trouvé pour `{stop_id}`.")
            return

        try:
            data: StopArea = StopArea.parse_raw(content)
        except Exception as e:
            logger.error(e)
            await inter.response.send_message(
                "❌ | Oops.. Quelque chose s'est mal passé..", ephemeral=True
            )
            return

        e: disnake.Embed = disnake.Embed(
            title=f"{data.name} ({data.city})",
            description="",
            colour=disnake.Colour.darker_grey(),
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

        if inter.response.is_done():
            await inter.edit_original_message(embed=e)
        else:
            await inter.response.send_message(embed=e)

    @commands.slash_command(description="Information sur une ligne.")
    async def info(self, inter: disnake.CommandInteraction):
        pass

    @info.sub_command(description="Information sur les trams — Code 🟣 🔴 🟤 ⚪")
    async def tram(
        self,
        inter: disnake.CommandInteraction,
        ligne: commands.option_enum(
            {
                "A": "line:TBT:59",
                "B": "line:TBT:60",
                "C": "line:TBT:61",
                "D": "line:TBT:62",
            },
        ),
    ):
        """A random command
        Parameters
        ----------
        inter: A random user
        ligne: Ligne de tram
        """
        await self._line_callback(inter, ligne)

    @info.sub_command(description="Information sur les Lianes — Code couleur 🟦 🟧 🟩")
    async def bus(
        self,
        inter: disnake.CommandInteraction,
        ligne: commands.Range[1, 99],
    ):
        """A random command
        Parameters
        ----------
        inter:
        ligne: Ligne de bus
        """
        line_id = f"line:TBC:{ligne:0>2}"
        await self._line_callback(inter, line_id)

    @info.sub_command(description="Information sur les arrêts")
    async def arret(
        self,
        inter: disnake.CommandInteraction,
        arret: str,
    ):
        """A random command
        Parameters
        ----------
        inter:
        arret: Nom de l'arrêt de bus/tram
        """
        status, content = await requester.search_for(arret)
        if status != 200 or content == "":
            logger.error(
                f"Unable to get any information for '{arret}'. Status returned: {status}."
            )
            await inter.response.send_message(
                f"❌ | Rien trouvé pour `{arret}`..", ephemeral=True
            )
            return

        try:
            search_result: Search = Search.parse_raw(content)
        except Exception as e:
            logger.error(e)
            await inter.response.send_message(
                "❌ | Oops.. Quelque chose s'est mal passé..", ephemeral=True
            )
            return

        stop_id: str = search_result.__root__[0].id
        await self._stop_callback(inter, stop_id)

    @arret.autocomplete("arret")
    async def stop_autocomplete(self, inter: disnake.CommandInteraction, string: str):
        status, content = await requester.search_for(string)
        if status != 200 or content == "":
            return []

        logger.debug(status)
        logger.debug(content)
        try:
            search_result: Search = Search.parse_raw(content)
            return [s.name for s in search_result.__root__ if s.is_stop]
        except Exception as e:
            logger.error(e)
            return []


def setup(bot):
    bot.add_cog(Information(bot))
