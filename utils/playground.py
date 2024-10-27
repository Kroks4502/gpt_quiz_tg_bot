import json

from openai.lib._parsing import type_to_response_format_param

from gpt.assistants.subtopic.schemas import Topics

if __name__ == "__main__":
    # Схема для https://platform.openai.com/playground/
    print(type_to_response_format_param(Topics)["json_schema"])
