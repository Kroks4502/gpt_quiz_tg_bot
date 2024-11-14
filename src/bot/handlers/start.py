import logging

from bot.constants import CQ_DATA_START, MAIN_MENU_BUTTON
from bot.handlers.quiz import handle_quiz_topic
from bot.manager import handlers_manager
from db.decorators import use_async_session_context
from db.models import User as DbUser
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient, events
from telethon.events import StopPropagation
from telethon.tl import custom
from telethon.tl.types import User

logger = logging.getLogger("bot.main")


@events.register(events.NewMessage(pattern="/start", incoming=True))
async def handle_start(event: events.NewMessage.Event | custom.Message):
    client: TelegramClient = event.client
    user_id = event.sender_id

    logger.debug("Processing command /start: user_id=%s", user_id)

    await register_user(event=event)

    await handlers_manager.remove_all(client, user_id)
    await handlers_manager.add(client, user_id, handle_quiz_topic, events.NewMessage(from_users=user_id, incoming=True))

    await event.respond("Придумай тему для квиза и отправь мне сообщение!", buttons=[[MAIN_MENU_BUTTON]])

    raise StopPropagation


@events.register(events.CallbackQuery(pattern=CQ_DATA_START))
async def handle_start_cq(event: events.CallbackQuery.Event):
    client: TelegramClient = event.client
    user_id = event.sender_id

    logger.debug("Processing command /start: user_id=%s", user_id)

    await register_user(event=event)

    await handlers_manager.remove_all(client, user_id)
    await handlers_manager.add(client, user_id, handle_quiz_topic, events.NewMessage(from_users=user_id, incoming=True))

    await client.edit_message(
        event.sender_id,
        event.message_id,
        "Придумай тему для квиза и отправь мне сообщение!",
        buttons=[[MAIN_MENU_BUTTON]],
    )

    raise StopPropagation


@use_async_session_context
async def register_user(session: AsyncSession, event: events.NewMessage.Event | custom.Message):
    db_user = await session.get(DbUser, event.sender_id)

    if db_user:
        return

    user: User = await event.get_sender()
    session.add(
        DbUser(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            phone=user.phone,
            lang_code=user.lang_code,
            usernames=str(user.usernames) if user.usernames else None,
        )
    )
    await session.commit()
