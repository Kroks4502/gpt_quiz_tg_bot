import logging

from bot.constants import CQ_DATA_MENU, CQ_DATA_MODE, CQ_DATA_TOPIC, NEW_QUIZ_BUTTON, Icon
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


@events.register(events.CallbackQuery(pattern=CQ_DATA_MENU))
async def handle_menu_cq(event: events.CallbackQuery.Event):
    client: TelegramClient = event.client
    await handlers_manager.remove_all(client, event.sender_id)
    await client.edit_message(event.sender_id, event.message_id, "Квиз-бот", **get_main_menu_buttons())
    raise StopPropagation


def get_main_menu_buttons():
    return dict(
        buttons=[
            [NEW_QUIZ_BUTTON],
            [Button.inline(text=f"{Icon.REPEAT} Мои темы", data=f"{CQ_DATA_TOPIC}.0")],
            [Button.inline(text=f"{Icon.SETTINGS} Параметры", data=CQ_DATA_MODE)],
        ]
    )
