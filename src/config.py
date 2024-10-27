import logging
import sys

from constants import ENV_FILE
from dotenv import load_dotenv
from pydantic import BaseModel, SecretStr, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

if ENV_FILE.exists() and ENV_FILE.is_file():
    load_dotenv(ENV_FILE)


class TelegramBot(BaseModel):
    api_id: SecretStr
    api_hash: SecretStr
    bot_token: SecretStr


class OpenAi(BaseModel):
    api_key: SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    telegram: TelegramBot
    openai: OpenAi


logger = logging.getLogger("app.settings")


try:
    settings = Settings()
except ValidationError as exc:

    def loc_to_dot_sep(loc) -> str:
        path = ""
        for i, x in enumerate(loc):
            if isinstance(x, str):
                if i > 0:
                    path += "."
                path += x
            elif isinstance(x, int):
                path += f"[{x}]"
            else:
                raise TypeError("Unexpected type")
        return path

    for err in exc.errors(include_url=False, include_context=False, include_input=False):
        field = loc_to_dot_sep(err["loc"])
        message = err["msg"]
        logger.error('Error in field "%s": %s', field, message)
    logger.critical("Error initializing settings from environment. Exiting app.")
    sys.exit(1)
