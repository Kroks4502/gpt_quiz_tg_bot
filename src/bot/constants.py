from enum import Enum


class Mode(str, Enum):
    SIMPLE = "simple"
    COMPLEX = "complex"


class Icon(str, Enum):
    SETTINGS = "⚙️"
    REPEAT = "🔁"

    TRUE = "✅"
    FALSE = "☑️"


CQ_DATA_MODE = "mode"
CQ_DATA_MODE_SIMPLE = f"{CQ_DATA_MODE}.{Mode.SIMPLE}"
CQ_DATA_MODE_COMPLEX = f"{CQ_DATA_MODE}.{Mode.COMPLEX}"

CQ_DATA_TOPIC = "topic"
