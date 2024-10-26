import logging

from telethon import events
from telethon.tl import custom

logger = logging.getLogger("bot.main")


@events.register(events.Raw())
async def handle_raw_debug(event: events.NewMessage.Event | custom.Message):
    logger.debug("Received Raw event: %s", event)
