from pydantic import BaseModel


class Topics(BaseModel):
    topics: list[str]


if __name__ == "__main__":
    # Схема для https://platform.openai.com/playground/
    import json
    from openai.lib._parsing import type_to_response_format_param
    print(json.dumps(type_to_response_format_param(Topics)["json_schema"]))
