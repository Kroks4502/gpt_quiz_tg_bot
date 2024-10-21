import logging

from bot.manager import handlers_manager
from telethon import TelegramClient, events
from telethon.events import StopPropagation
from telethon.tl import custom

logger = logging.getLogger("bot.main")


@events.register(events.NewMessage(pattern="/stop", incoming=True))
async def handle_stop(event: events.NewMessage.Event | custom.Message):
    client: TelegramClient = event.client
    user_id = event.sender_id

    logger.debug("Processing command /stop: user_id=%s", user_id)

    removed_hs = await handlers_manager.remove_all(client, event.sender_id)
    if removed_hs > 0:
        await event.respond(f"Согласен, хватит! 🫶")
    else:
        await event.respond("Нечего останавливать 🤔")

    raise StopPropagation
