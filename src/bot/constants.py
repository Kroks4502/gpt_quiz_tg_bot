from enum import Enum

from telethon import Button


class Mode(str, Enum):
    SIMPLE = "simple"
    COMPLEX = "complex"


class Icon(str, Enum):
    SETTINGS = "⚙️"
    REPEAT = "🔁"

    TRUE = "✅"
    FALSE = "☑️"

    PREV = "⬅️"
    NEXT = "➡️"

    MENU = "🎛"

    START = "🚀"


CQ_DATA_MENU = "menu"
CQ_DATA_START = "start"

CQ_DATA_MODE = "mode"
CQ_DATA_MODE_SIMPLE = f"{CQ_DATA_MODE}.{Mode.SIMPLE}"
CQ_DATA_MODE_COMPLEX = f"{CQ_DATA_MODE}.{Mode.COMPLEX}"

CQ_DATA_TOPIC = "topic"

NEW_QUIZ_BUTTON = Button.inline(text=f"{Icon.START} Новый квиз", data=CQ_DATA_START)
MAIN_MENU_BUTTON = Button.inline(text="Меню", data=CQ_DATA_MENU)
