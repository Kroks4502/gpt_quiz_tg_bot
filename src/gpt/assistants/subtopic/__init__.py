import copy
import logging
from pathlib import Path

from db.manager import sessionmanager
from db.models import AssistantHistory
from gpt.assistants.subtopic.schemas import Topics
from gpt.client import client
from openai import LengthFinishReasonError, OpenAIError
from openai.lib._parsing import type_to_response_format_param

ASSISTANT_NAME = "subtopic"
MODEL_PARAMS = dict(
    model="gpt-4o-mini",
    temperature=0.7,
    top_p=1,
    max_tokens=2048,
    response_format=Topics,
)
MAX_ATTEMPT = 3
PROMPT_DIR = Path(__file__).parent / "prompt"

with open(PROMPT_DIR / "system", "r") as file:
    PROMPT_SYS = file.read()

logger = logging.getLogger(f"gpt.{ASSISTANT_NAME}")


async def create_subtopics(topic: str, *, attempt: int = 0) -> list[str]:
    attempt += 1
    logger.debug("Creating subtopics, topic=%s, attempt=%s", topic, attempt)

    if attempt > MAX_ATTEMPT:
        msg = f"Exceeded maximum number of attempts ({MAX_ATTEMPT}) to create poll."
        logger.error(msg)
        raise RuntimeError(msg)

    messages = [
        {
            "role": "system",
            "content": PROMPT_SYS,
        },
        {
            "role": "user",
            "content": topic,
        },
    ]

    try:
        response = await client.beta.chat.completions.parse(messages=messages, **MODEL_PARAMS)

    except LengthFinishReasonError as err:
        logger.error(f"Too many tokens: {err}")
        await register_assistant_history(messages, None, "LengthFinishReasonError")
        return await create_subtopics(topic, attempt=attempt)

    except OpenAIError as err:
        logger.error(f"Unexpected error: {err}")
        await register_assistant_history(messages, None, "OpenAIError")
        return await create_subtopics(topic, attempt=attempt)

    gpt_result = response.choices[-1].message

    # If the model refuses to respond, you will get a refusal message
    if gpt_result.refusal:
        await register_assistant_history(messages, gpt_result.content, "refusal")
        return await create_subtopics(topic, attempt=attempt)

    if not gpt_result.parsed:
        logger.debug("Subtopic creation failed, message.content=%s", gpt_result.content)
        await register_assistant_history(messages, gpt_result.content, "not parsed")
        return await create_subtopics(topic, attempt=attempt)

    subtopics = gpt_result.parsed.topics
    logger.debug("Subtopics created successfully: %s", subtopics)
    await register_assistant_history(messages, gpt_result.parsed.model_dump())
    return subtopics


async def register_assistant_history(
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
                prompt_params=None,
                messages=messages,
                result=result,
                error=error,
            )
        )
        await session.commit()
