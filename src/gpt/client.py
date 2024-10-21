import logging
import os

from openai import AsyncOpenAI

logger = logging.getLogger("gpt")
logger.setLevel(logging.DEBUG)

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
