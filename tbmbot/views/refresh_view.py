import asyncio
from datetime import datetime
from typing import Optional

import disnake
from loguru import logger
from tbmbot.models import Schedule as Schedule_m
from tbmbot.utils import embeds, requester, tram_converter


class RefreshView(disnake.ui.View):
    def __init__(
        self,
        stop_line_ids: list,
        stop_name: str,
        stop_city: str,
        *,
        timeout: Optional[float] = 180,
    ):
        super().__init__(timeout=timeout)
        self.stop_line_ids = stop_line_ids
        self.stop_name: str = stop_name
        self.stop_city: str = stop_city

    @disnake.ui.button(label="🔁 Rafraichir", style=disnake.ButtonStyle.blurple)
    async def refresh_schedules(
        self, button: disnake.ui.Button, interaction: disnake.InteractionMessage
    ):
        schedule_list: list = []
        schedule_requests: list = []

        for s_id, l_ids in self.stop_line_ids:
            for l_name, l_id in l_ids:
                schedule_requests.append(
                    requester.get_stop_schedule(
                        l_name, s_id, tram_converter.get_tram_schedule_id(l_id)
                    )
                )

        responses = await asyncio.gather(*schedule_requests, return_exceptions=True)
        for status, content in responses:
            if status != 200 or content == requester.EMPTY_RESPONSE:
                continue
            logger.debug(content)
            try:
                schedule_data: Schedule_m = Schedule_m.parse_raw(content)
                logger.debug(schedule_data)
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
            f"⌚ {self.stop_name} — {self.stop_city}", schedule_list
        )
        date = datetime.now()
        e.set_footer(text=f"Dernière mise à jour à {date.strftime('%H:%M:%S')}")

        # Make sure to update the message with our updated selves
        await interaction.response.edit_message(embed=e, view=self)
