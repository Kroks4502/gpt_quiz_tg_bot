import logging

from bot.constants import CQ_DATA_MODE, CQ_DATA_TOPIC, Icon
from bot.manager import handlers_manager
from telethon import Button, TelegramClient, events
from telethon.events import StopPropagation
from telethon.tl import custom

logger = logging.getLogger("bot.menu")


@events.register(events.NewMessage(pattern="/menu", incoming=True))
async def handle_menu(event: events.NewMessage.Event | custom.Message):
    client: TelegramClient = event.client

    logger.debug("Processing command /menu: user_id=%s", event.sender_id)

    await handlers_manager.remove_all(client, event.sender_id)

    await client.send_message(event.sender_id, "Квиз-бот", **get_main_menu_buttons())

    raise StopPropagation


def get_main_menu_buttons():
    return dict(
        buttons=[
            [Button.inline(text=f"{Icon.SETTINGS} Режим квиза", data=CQ_DATA_MODE)],
            [Button.inline(text=f"{Icon.REPEAT} Предыдущие темы", data=CQ_DATA_TOPIC)],
        ]
    )
