import asyncio
import logging.config

from src.bot import BotHandler
from src.core import LOGGING_CONFIG, application_settings
from src.monitoring_agent import start_prometheus

logging.config.dictConfig(LOGGING_CONFIG)


async def main():
    bot_task = asyncio.create_task(BotHandler(application_settings.APP_TELEGRAM_KEY).start())
    prometheus_task = asyncio.create_task(start_prometheus())
    await asyncio.gather(bot_task, prometheus_task)


if __name__ == '__main__':
    asyncio.run(main())
