import os

import nextcord

from dotenv import load_dotenv
from loguru import logger
from nextcord.ext import commands

from tbmbot import TBMBot
from tbmbot.cogs import __extensions__


def main():
    load_dotenv(".env")
    bot = TBMBot(
        command_prefix=" ",
        activity=nextcord.Activity(
            name="bus vroom vroom",
            type=nextcord.ActivityType.watching,
        ),
    )

    for e in __extensions__:
        try:
            bot.load_extension(name=f"{e['package']}.{e['name']}")
            logger.success(f"Extension '{e['package']}.{e['name']}' loaded")
        except commands.ExtensionNotFound as e:
            logger.error(e)

    logger.info("Launching bot...")
    bot.run(token=os.environ["BOT_TOKEN"])


if __name__ == "__main__":
    main()
