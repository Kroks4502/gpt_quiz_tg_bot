import asyncio

from dotenv import load_dotenv

from src.config import configure_logging
from src.constants import ENV_FILE

if __name__ == '__main__':
    configure_logging()

    if ENV_FILE.exists() and ENV_FILE.is_file():
        load_dotenv(ENV_FILE)

    from bot.client import (run_bot)
    asyncio.run(run_bot())

    # from gpt.assistants.question import create_question
    # asyncio.run(create_question("Мошенники в интернете", []))

    # from gpt.assistants.subtopic import create_subtopics
    # asyncio.run(create_subtopics("Мошенники в интернете"))
