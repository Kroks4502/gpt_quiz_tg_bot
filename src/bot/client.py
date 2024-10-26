import logging
import os
import platform

from bot.handlers.debug import handle_raw_debug
from bot.handlers.start import handle_start
from bot.handlers.stop import handle_stop
from bot.handlers.unknown import handle_unknown
from telethon import TelegramClient

logger = logging.getLogger("bot")

client: TelegramClient = TelegramClient(
    session="eng_gpt_bot",
    api_id=int(os.getenv("TG_API_ID")),
    api_hash=os.getenv("TG_API_HASH"),
    auto_reconnect=True,
    device_model=f"{platform.python_implementation()} {platform.python_version()}",
    system_version=f"{platform.system()} {platform.release()}",
    app_version="eng_gpt_bot v.0.0.1",
)


def setup_handlers():
    client.add_event_handler(handle_raw_debug)
    client.add_event_handler(handle_start)
    client.add_event_handler(handle_stop)
    client.add_event_handler(handle_unknown)


async def run_bot():
    await client.start(bot_token=os.getenv("TG_BOT_TOKEN"))
    setup_handlers()

    await client.run_until_disconnected()
