import asyncio

from log import configure_logging

if __name__ == "__main__":
    configure_logging()

    from bot.client import run_bot

    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        pass

    # from gpt.assistants.question import create_question
    # asyncio.run(create_question("Мошенники в интернете", []))

    # from gpt.assistants.subtopic import create_subtopics
    # asyncio.run(create_subtopics("Мошенники в интернете"))
