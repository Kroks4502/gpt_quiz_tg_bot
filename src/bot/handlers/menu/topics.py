from bot.constants import CQ_DATA_TOPIC
from bot.handlers.quiz import process_quiz
from db.manager import sessionmanager
from db.models import UserTopic
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import Button, TelegramClient, events
from telethon.events import StopPropagation


@events.register(events.CallbackQuery(data=CQ_DATA_TOPIC))
async def handle_menu_topics(event: events.CallbackQuery.Event):
    client: TelegramClient = event.client

    stmt = (
        select(func.min(UserTopic.id).label("id"), UserTopic.topic.label("topic"))
        .where(UserTopic.user_id == event.sender_id)
        .group_by(UserTopic.topic)
        .limit(10)
    )
    async with sessionmanager.session() as session:
        session: AsyncSession
        result = await session.execute(stmt)
        buttons = [[Button.inline(text=t.topic, data=f"{CQ_DATA_TOPIC}.{t.id}")] for t in result.all()]

    await client.edit_message(
        event.sender_id,
        event.message_id,
        "Выберите предыдущую тему для старта нового квиза:",
        buttons=buttons,
    )

    raise StopPropagation


@events.register(events.CallbackQuery(pattern=rf"{CQ_DATA_TOPIC}\.(\d+)"))
async def handle_menu_choice_topic(event: events.CallbackQuery.Event):
    client: TelegramClient = event.client

    topic_id = int(event.data_match.group(1))

    async with sessionmanager.session() as session:
        session: AsyncSession
        topic = await session.get(UserTopic, topic_id)

    topic_name = topic.topic
    await event.answer(f'Начинаем квиз на тему "{topic_name}"')

    await process_quiz(client, event.sender_id, topic_name)

    raise StopPropagation
