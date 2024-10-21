import json
import logging
import random
from json import JSONDecodeError
from pathlib import Path

from gpt.assistants.question.models import QuizQuestion, QuizQuestionGpt, UserAnswer
from gpt.client import client
from openai import LengthFinishReasonError, OpenAIError
from pydantic import ValidationError

logger = logging.getLogger("gpt.question")

NUMBER_ANSWER_OPTIONS = {
    "two": 20,
    "three": 25,
    "four": 25,
    "five": 15,
    "six": 5,
    "seven": 3,
    "eight": 3,
}
MAX_ATTEMPT = 3
PROMPT_DIR = Path(__file__).parent / "prompt"

with open(PROMPT_DIR / "system", "r") as file:
    PROMPT_SYS = file.read()

with open(PROMPT_DIR / "not-repeat", "r") as file:
    PROMPT_NOT_REPEAT = file.read()

with open(PROMPT_DIR / "user", "r") as file:
    PROMPT_USER = file.read()


async def create_question(topic: str, subtopic: str, prev_answers: list[UserAnswer], *, attempt: int = 0) -> QuizQuestion:
    attempt += 1
    logger.debug("Creating poll, topic=%s, prev_answers=%s, attempt=%s", topic, prev_answers, attempt)

    if attempt > MAX_ATTEMPT:
        msg = f"Exceeded maximum number of attempts ({MAX_ATTEMPT}) to create poll."
        logger.error(msg)
        raise RuntimeError(msg)

    gpt_result = await _get_question(topic, subtopic, prev_answers)

    try:
        data = json.loads(gpt_result)
    except JSONDecodeError as err:
        logger.warning(f"JSONDecodeError: {err}")
        return await create_question(topic, subtopic, prev_answers, attempt=attempt)

    try:
        question = QuizQuestion(**data)
    except ValidationError as err:
        logger.warning(f"ValidationError: {err}")
        return await create_question(topic, subtopic, prev_answers, attempt=attempt)

    logger.debug("Poll created successfully: %s", question)

    return question


async def _get_question(topic: str, subtopic: str, prev_answers: list[UserAnswer]) -> str:
    try:
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": _get_system_prompt(prev_answers),
                },
                {
                    "role": "user",
                    "content": PROMPT_USER.format(topic=topic, subtopic=subtopic),
                },
            ],
            temperature=0.7,
            top_p=1,
            max_tokens=512,
            response_format=QuizQuestionGpt,
        )

        message = response.choices[-1].message

        # If the model refuses to respond, you will get a refusal message
        if message.refusal:
            return ""

        return message.content

    except LengthFinishReasonError as err:
        logger.error(f"Too many tokens: {err}")

    except OpenAIError as err:
        logger.error(f"Unexpected error: {err}")

    return ""


def _get_system_prompt(prev_answers: list[UserAnswer]):
    prompt = [
        PROMPT_SYS.format(
            number=random.choices(list(NUMBER_ANSWER_OPTIONS.keys()), weights=list(NUMBER_ANSWER_OPTIONS.values()))
        )
    ]

    if prev_answers:
        prompt.append(PROMPT_NOT_REPEAT.format(prev_answers="\n- ".join([a.question for a in prev_answers])))

    return "\n\n".join(prompt)
