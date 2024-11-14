import logging
import random
from asyncio import sleep
from datetime import datetime

from bot.constants import Mode
from bot.manager import handlers_manager
from db.decorators import use_async_session_context
from db.manager import sessionmanager
from db.models import User, UserTopic
from gpt.assistants.question import UserAnswer, create_question
from gpt.assistants.subtopic import create_subtopics
from sqlalchemy.ext.asyncio import AsyncSession
from telethon import TelegramClient, events
from telethon.events import StopPropagation
from telethon.tl import custom
from telethon.tl.types import (
    MessageMediaPoll,
    Poll,
    PollAnswer,
    PollAnswerVoters,
    PollResults,
    TextWithEntities,
    UpdateMessagePoll,
)

logger = logging.getLogger("bot.quiz")
PERIOD_Q = 15
SLEEP_DELAY = 5
MAX_PREV_ANSWER = 20


async def handle_quiz_topic(event: events.NewMessage.Event | custom.Message):
    client: TelegramClient = event.client
    user_id = event.sender_id

    logger.debug("Processing quiz topic: user_id=%s", user_id)

    topic = event.text

    await process_quiz(client, user_id, topic)


async def process_quiz(client: TelegramClient, user_id: int, topic: str):
    async with sessionmanager.session() as session:
        session: AsyncSession
        user = await session.get(User, user_id)
        await session.commit()

    subtopics = await create_subtopics(topic) if user.bot_mode == Mode.COMPLEX else []
    logger.debug("Subtopics created: user_id=%s, topic=%s, subtopics=%s", user_id, topic, subtopics)

    await register_user_subtopics(user_id=user_id, topic=topic, subtopics=subtopics)

    await send_quiz(client, user_id, topic, subtopics, [])


async def send_quiz(client: TelegramClient, user_id, topic: str, subtopics: list[str], prev_answers: list[UserAnswer]):
    random_subtopic = random.choice(subtopics) if subtopics else None
    logger.info(
        "Creating quiz: user_id=%s, topic=%s, random_subtopic=%s, prev_answers=%s",
        user_id,
        topic,
        random_subtopic,
        prev_answers,
    )

    await handlers_manager.remove_all(client, user_id)

    if len(prev_answers) > MAX_PREV_ANSWER:
        prev_answers = prev_answers[1:]

    question = await create_question(topic, random_subtopic, prev_answers)
    # question = QuizQuestion(title=random_subtopic, answers=["A", "B"], correct_answer=1, solution="solution")
    close_period = len(question.answers) * PERIOD_Q
    quiz_msg = await client.send_message(
        entity=user_id,
        file=MessageMediaPoll(
            poll=Poll(
                id=random.randint(0, 100_000),
                question=TextWithEntities(question.title, entities=[]),
                answers=[
                    PollAnswer(TextWithEntities(text, entities=[]), bytes(idx))
                    for idx, text in enumerate(question.answers, start=1)
                ],
                quiz=True,
                close_period=close_period,
            ),
            results=PollResults(
                results=[PollAnswerVoters(option=bytes(question.correct_answer + 1), voters=200_000, correct=True)],
                solution=question.solution,
                solution_entities=[] if question.solution else None,
            ),
        ),
    )
    poll_id = quiz_msg.media.poll.id
    logger.debug("Sent poll: user_id=%s, poll_id=%s", user_id, poll_id)

    async def check_answer_and_next(poll: Poll, poll_results: PollResults):
        correct = False
        for answer in poll_results.results:
            if answer.voters == 1:
                correct = answer.correct
        prev_answers.append(UserAnswer(question=poll.question.text, correct=correct))
        await send_quiz(client, user_id, topic, subtopics, prev_answers)

    async def handle_answer(event: UpdateMessagePoll):
        logger.debug("Processing answer: user_id=%s, event=%s", user_id, event)
        await check_answer_and_next(event.poll, event.results)
        raise StopPropagation

    event_answer = events.Raw(
        types=UpdateMessagePoll,
        func=lambda e: quiz_msg.media.poll.id == e.poll_id,
    )
    await handlers_manager.add(client, user_id, handle_answer, event_answer)

    async def has_answered() -> bool:
        logger.debug("Update poll message: user_id=%s, poll_id=%s", user_id, poll_id)
        upd_quiz_msg = await client.get_messages(user_id, ids=quiz_msg.id)
        if upd_quiz_msg.media.results.total_voters != 0:
            await check_answer_and_next(upd_quiz_msg.media.poll, upd_quiz_msg.media.results)
            return True

        return False

    start_dt = datetime.now()
    while (datetime.now() - start_dt).seconds < close_period:
        if not handlers_manager.have_active_handler(user_id, handle_answer, event_answer) or await has_answered():
            raise StopPropagation
        await sleep(SLEEP_DELAY)

    if not handlers_manager.have_active_handler(user_id, handle_answer, event_answer) or await has_answered():
        raise StopPropagation

    logger.debug("Time's up: user_id=%s, poll_id=%s", user_id, poll_id)

    if handlers_manager.have_active_handler(user_id, handle_answer, event_answer):
        logger.debug("User didn't have time to answer the question: user_id=%s, poll_id=%s", user_id, poll_id)

        await handlers_manager.remove_all(client, user_id)

        prev_answers.append(UserAnswer(question=question.title, correct=False))

        await client.send_message(
            entity=user_id,
            message=(
                f"Ой, время вышло. Твой текущий результат {len([a for a in prev_answers if a.correct])}"
                f"/{len(prev_answers)}, но ты можешь продолжить /continue или начать новый квиз /start"
            ),
        )

        async def handle_continue(_):
            logger.debug("Processing command /continue: user_id=%s, poll_id=%s", user_id, poll_id)

            await send_quiz(client, user_id, topic, subtopics, prev_answers)
            raise StopPropagation

        async def handle_unknown(event):
            logger.debug("Processing unknown message: user_id=%s, poll_id=%s, event=%s", user_id, poll_id, event)

            await client.send_message(
                entity=user_id,
                message="Ты можешь продолжить предыдущий квиз /continue или начать новый /start",
            )
            raise StopPropagation

        await handlers_manager.add(
            client=client,
            user_id=user_id,
            callback=handle_continue,
            event=events.NewMessage(
                pattern="/continue",
                from_users=user_id,
                incoming=True,
            ),
        )
        await handlers_manager.add(
            client=client,
            user_id=user_id,
            callback=handle_unknown,
            event=events.NewMessage(
                from_users=user_id,
                incoming=True,
            ),
        )

    raise StopPropagation


@use_async_session_context
async def register_user_subtopics(session: AsyncSession, user_id: int, topic: str, subtopics: list[str]) -> None:
    session.add(
        UserTopic(
            user_id=user_id,
            topic=topic,
            subtopics=subtopics,
        )
    )
    await session.commit()
