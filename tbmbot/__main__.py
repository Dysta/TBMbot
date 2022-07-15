import os

import disnake

from dotenv import load_dotenv
from loguru import logger
from disnake.ext import commands

from tbmbot import TBMBot
from tbmbot.cogs import __extensions__


def main():
    load_dotenv(".env")
    bot = TBMBot(
        test_guilds=[492677155180904448],
        activity=disnake.Activity(
            name="bus vroom vroom",
            type=disnake.ActivityType.watching,
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
