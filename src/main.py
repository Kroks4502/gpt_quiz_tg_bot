import asyncio
import logging

from bot.client import run_bot
from db.manager import sessionmanager
from log import configure_logging

logger = logging.getLogger("app")

if __name__ == "__main__":
    configure_logging()

    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Application termination initiated by user.")
    finally:
        if sessionmanager._engine is not None:
            # Close the DB connection
            asyncio.run(sessionmanager.close())
