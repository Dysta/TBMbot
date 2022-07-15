import traceback

from disnake.ext import commands
from loguru import logger


class TBMBot(commands.InteractionBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_ready(self):
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")

    async def on_error(self, event, *args, **kwargs):
        logger.error(f"{event=}{args}{kwargs}")
        traceback.print_exc()
