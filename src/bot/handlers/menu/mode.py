from bot.constants import CQ_DATA_MODE, CQ_DATA_MODE_COMPLEX, CQ_DATA_MODE_SIMPLE, Icon, Mode
from db.manager import sessionmanager
from db.models import User
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import Button, TelegramClient, events
from telethon.events import StopPropagation


@events.register(events.CallbackQuery(data=CQ_DATA_MODE))
async def handle_menu_mode(event: events.CallbackQuery.Event):
    client: TelegramClient = event.client

    async with sessionmanager.session() as session:
        session: AsyncSession
        user = await session.get(User, event.sender_id)
        await session.commit()

    if user.bot_mode == Mode.SIMPLE:
        icon_simple, icon_complex = Icon.TRUE, Icon.FALSE
    elif user.bot_mode == Mode.COMPLEX:
        icon_simple, icon_complex = Icon.FALSE, Icon.TRUE
    else:
        icon_simple, icon_complex = Icon.FALSE, Icon.FALSE

    await client.edit_message(
        event.sender_id,
        event.message_id,
        "Квиз-бот для создания вопросов может использовать больше тем на основе предложенной вами.\n\nВыберите режим:",
        buttons=[
            [Button.inline(text=f"{icon_simple} Строго придерживаться темы", data=CQ_DATA_MODE_SIMPLE)],
            [Button.inline(text=f"{icon_complex}️ Трактовать тему более широко", data=CQ_DATA_MODE_COMPLEX)],
        ],
    )

    raise StopPropagation


@events.register(events.CallbackQuery(data=CQ_DATA_MODE_SIMPLE))
async def handle_menu_mode_set_simple(event: events.CallbackQuery.Event):
    client: TelegramClient = event.client

    stmt = update(User).where(User.id == event.sender_id).values(bot_mode=Mode.SIMPLE)
    async with sessionmanager.session() as session:
        await session.execute(stmt)
        await session.commit()

    await client.edit_message(
        event.sender_id,
        event.message_id,
        f"{Icon.TRUE} Квиз-бот будет генерировать вопросы только по теме, которую вы предложите.",
    )

    raise StopPropagation


@events.register(events.CallbackQuery(data=CQ_DATA_MODE_COMPLEX))
async def handle_menu_mode_set_complex(event: events.CallbackQuery.Event):
    client: TelegramClient = event.client

    stmt = update(User).where(User.id == event.sender_id).values(bot_mode=Mode.COMPLEX)
    async with sessionmanager.session() as session:
        await session.execute(stmt)
        await session.commit()

    await client.edit_message(
        event.sender_id,
        event.message_id,
        f"{Icon.TRUE} Квиз-бот будет широко трактовать тему, которую вы предложите.",
    )

    raise StopPropagation
