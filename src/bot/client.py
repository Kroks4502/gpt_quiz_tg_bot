import platform

from bot.handlers.debug import handle_raw_debug
from bot.handlers.menu.main import handle_menu, handle_menu_cq
from bot.handlers.menu.mode import handle_menu_mode, handle_menu_mode_set_complex, handle_menu_mode_set_simple
from bot.handlers.menu.topics import handle_menu_choice_topic, handle_menu_topics
from bot.handlers.start import handle_start, handle_start_cq
from bot.handlers.stop import handle_stop
from bot.handlers.unknown import handle_unknown
from config import settings
from telethon import TelegramClient

client: TelegramClient = TelegramClient(
    session="eng_gpt_bot",
    api_id=settings.telegram.api_id.get_secret_value(),
    api_hash=settings.telegram.api_hash.get_secret_value(),
    auto_reconnect=True,
    device_model=f"{platform.python_implementation()} {platform.python_version()}",
    system_version=f"{platform.system()} {platform.release()}",
    app_version="eng_gpt_bot v.0.0.1",
)


def setup_handlers():
    client.add_event_handler(handle_raw_debug)

    client.add_event_handler(handle_start)
    client.add_event_handler(handle_stop)
    client.add_event_handler(handle_menu)

    client.add_event_handler(handle_menu_cq)
    client.add_event_handler(handle_start_cq)
    client.add_event_handler(handle_menu_mode)
    client.add_event_handler(handle_menu_mode_set_simple)
    client.add_event_handler(handle_menu_mode_set_complex)
    client.add_event_handler(handle_menu_topics)
    client.add_event_handler(handle_menu_choice_topic)

    client.add_event_handler(handle_unknown)


async def run_bot():
    await client.start(bot_token=settings.telegram.bot_token.get_secret_value())
    setup_handlers()

    await client.run_until_disconnected()
