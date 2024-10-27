import copy
import json
import logging
import random
from json import JSONDecodeError
from pathlib import Path

from db.manager import sessionmanager
from db.models import AssistantHistory
from gpt.assistants.question.schemas import QuizQuestion, QuizQuestionGpt, UserAnswer
from gpt.client import client
from openai import LengthFinishReasonError, OpenAIError
from openai.lib._parsing import type_to_response_format_param
from pydantic import ValidationError

ASSISTANT_NAME = "question"
MODEL_PARAMS = dict(
    model="gpt-4o-mini",
    temperature=0.7,
    top_p=1,
    max_tokens=512,
    response_format=QuizQuestionGpt,
)
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

logger = logging.getLogger(f"gpt.{ASSISTANT_NAME}")


async def create_question(
    topic: str,
    subtopic: str,
    prev_answers: list[UserAnswer],
    *,
    attempt: int = 0,
) -> QuizQuestion:
    attempt += 1
    logger.debug("Creating poll, topic=%s, prev_answers=%s, attempt=%s", topic, prev_answers, attempt)

    if attempt > MAX_ATTEMPT:
        msg = f"Exceeded maximum number of attempts ({MAX_ATTEMPT}) to create poll."
        logger.error(msg)
        raise RuntimeError(msg)

    number_options = random.choices(list(NUMBER_ANSWER_OPTIONS.keys()), weights=list(NUMBER_ANSWER_OPTIONS.values()))
    prompt_params = {
        "number_options": number_options,
        "topic": topic,
        "subtopic": subtopic,
        "prev_answers": [answer.model_dump() for answer in prev_answers],
    }
    messages = [
        {
            "role": "system",
            "content": _get_system_prompt(prev_answers, number_options),
        },
        {
            "role": "user",
            "content": PROMPT_USER.format(topic=topic, subtopic=subtopic),
        },
    ]

    try:
        response = await client.beta.chat.completions.parse(messages=messages, **MODEL_PARAMS)

    except LengthFinishReasonError as err:
        logger.error(f"Too many tokens: {err}")
        await register_assistant_history(prompt_params, messages, None, "LengthFinishReasonError")
        return await create_question(topic, subtopic, prev_answers, attempt=attempt)

    except OpenAIError as err:
        logger.error(f"Unexpected error: {err}")
        await register_assistant_history(prompt_params, messages, None, "OpenAIError")
        return await create_question(topic, subtopic, prev_answers, attempt=attempt)

    gpt_result = response.choices[-1].message

    # If the model refuses to respond, you will get a refusal message
    if gpt_result.refusal:
        await register_assistant_history(prompt_params, messages, gpt_result.content, "refusal")
        return await create_question(topic, subtopic, prev_answers, attempt=attempt)

    if not gpt_result.parsed:
        logger.debug("Question creation failed, message.content=%s", gpt_result.content)
        await register_assistant_history(prompt_params, messages, gpt_result.content, "not parsed")
        return await create_question(topic, subtopic, prev_answers, attempt=attempt)

    try:
        data = json.loads(gpt_result.content)
    except JSONDecodeError as err:
        logger.warning(f"JSONDecodeError: {err}")
        await register_assistant_history(prompt_params, messages, gpt_result.content, "JSONDecodeError")
        return await create_question(topic, subtopic, prev_answers, attempt=attempt)

    try:
        question = QuizQuestion(**data)
    except ValidationError as err:
        logger.warning(f"ValidationError: {err}")
        await register_assistant_history(prompt_params, messages, gpt_result.content, "ValidationError")
        return await create_question(topic, subtopic, prev_answers, attempt=attempt)

    logger.debug("Poll created successfully: %s", question)
    await register_assistant_history(prompt_params, messages, gpt_result.parsed.model_dump())

    return question


def _get_system_prompt(prev_answers: list[UserAnswer], number: str):
    prompt = [PROMPT_SYS.format(number=number)]

    if prev_answers:
        prompt.append(PROMPT_NOT_REPEAT.format(prev_answers="\n- ".join([a.question for a in prev_answers])))

    return "\n\n".join(prompt)


async def register_assistant_history(
    prompt_params: dict[str, str],
    messages: list[dict[str, str]],
    result: dict | list | str | None,
    error: str = None,
) -> None:
    model_params = copy.copy(MODEL_PARAMS)
    model_params["response_format"] = type_to_response_format_param(model_params["response_format"])["json_schema"]
    async with sessionmanager.session() as session:
        session.add(
            AssistantHistory(
                assistant=ASSISTANT_NAME,
                model_params=model_params,
                prompt_params=prompt_params,
                messages=messages,
                result=result,
                error=error,
            )
        )
        await session.commit()
