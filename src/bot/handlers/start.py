import logging

from bot.handlers.quiz import handle_quiz_topic
from bot.manager import handlers_manager
from telethon import TelegramClient, events
from telethon.events import StopPropagation
from telethon.tl import custom

logger = logging.getLogger("bot.main")


@events.register(events.NewMessage(pattern="/start", incoming=True))
async def handle_start(event: events.NewMessage.Event | custom.Message):
    client: TelegramClient = event.client
    user_id = event.sender_id

    logger.debug("Processing command /start: user_id=%s", user_id)

    await handlers_manager.remove_all(client, user_id)
    await handlers_manager.add(client, user_id, handle_quiz_topic, events.NewMessage(from_users=user_id, incoming=True))

    await event.respond("Придумай тему для квиза и отправь мне!")

    raise StopPropagation
