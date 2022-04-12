from . import __TESTING_GUILDS_ID__

import nextcord

from loguru import logger
from nextcord.ext import commands

from tbmbot.models import LineInformation, Alerts
from tbmbot.utils import embeds, requester


class Information(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @staticmethod
    async def _callback(inter: nextcord.Interaction, opts: str):
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

        if inter.response.is_done():
            await inter.edit_original_message(embed=e, view=None)
        else:
            await inter.response.send_message(embeds=embed_to_send)

    @nextcord.slash_command(
        guild_ids=__TESTING_GUILDS_ID__, description="Information sur une ligne."
    )
    async def info(self, inter: nextcord.Interaction):
        pass

    @info.subcommand(description="Information sur les trams — Code 🟣 🔴 🟤 ⚪")
    async def tram(
        self,
        inter: nextcord.Interaction,
        opts: str = nextcord.SlashOption(
            name="ligne",
            description="Ligne de tram - ",
            required=True,
            choices={
                "A": "line:TBT:59",
                "B": "line:TBT:60",
                "C": "line:TBT:64",
                "D": "line:TBT:62",
            },
        ),
    ):
        await self._callback(inter, opts)

    @info.subcommand(description="Information sur les Lianes — Code couleur 🟦 🟧 🟩")
    async def bus(
        self,
        inter: nextcord.Interaction,
        opts: int = nextcord.SlashOption(
            name="ligne",
            description="Numéro de la ligne 🟦 🟧 🟩",
            required=True,
            min_value=1,
            max_value=99,
        ),
    ):
        opts = f"line:TBC:{opts:0>2}"
        await self._callback(inter, opts)


def setup(bot):
    bot.add_cog(Information(bot))
