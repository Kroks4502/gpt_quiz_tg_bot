import logging

from bot.manager import handlers_manager
from telethon import TelegramClient, events
from telethon.events import StopPropagation
from telethon.tl import custom

logger = logging.getLogger("bot.main")


@events.register(events.NewMessage(incoming=True))
async def handle_unknown(event: events.NewMessage.Event | custom.Message):
    client: TelegramClient = event.client
    user_id = event.sender_id

    logger.debug("Processing unknown message: user_id=%s, event=%s", user_id, event)

    if handlers_manager.have_active_handler(user_id):
        return

    await event.respond("Хочешь начать новый квиз? Просто отправь мне /start")

    raise StopPropagation
