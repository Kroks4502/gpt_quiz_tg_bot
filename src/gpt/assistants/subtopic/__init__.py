import logging
from pathlib import Path

from gpt.assistants.subtopic.schemas import Topics
from gpt.client import client
from openai import LengthFinishReasonError, OpenAIError

logger = logging.getLogger("gpt.subtopic")

MAX_ATTEMPT = 3
PROMPT_DIR = Path(__file__).parent / "prompt"

with open(PROMPT_DIR / "system", "r") as file:
    PROMPT_SYS = file.read()


async def create_subtopics(topic: str, *, attempt: int = 0) -> list[str]:
    attempt += 1
    logger.debug("Creating subtopics, topic=%s, attempt=%s", topic, attempt)

    if attempt > MAX_ATTEMPT:
        msg = f"Exceeded maximum number of attempts ({MAX_ATTEMPT}) to create poll."
        logger.error(msg)
        raise RuntimeError(msg)

    try:
        response = await client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": PROMPT_SYS,
                },
                {
                    "role": "user",
                    "content": topic,
                },
            ],
            temperature=0.7,
            top_p=1,
            max_tokens=2048,
            response_format=Topics,
        )

        message = response.choices[-1].message

        # If the model refuses to respond, you will get a refusal message
        if message.refusal:
            return await create_subtopics(topic, attempt=attempt)

        if message.parsed:
            subtopics = message.parsed.topics
            logger.debug("Subtopics created successfully: %s", subtopics)
            return subtopics

        logger.debug("Subtopic creation failed, message.content=%s", message.content)

    except LengthFinishReasonError as err:
        logger.error(f"Too many tokens: {err}")

    except OpenAIError as err:
        logger.error(f"Unexpected error: {err}")

    return await create_subtopics(topic, attempt=attempt)
