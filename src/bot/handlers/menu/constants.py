from enum import StrEnum


class Mode(StrEnum):
    SIMPLE = "simple"
    COMPLEX = "complex"


CQ_DATA_MODE = "mode"
CQ_DATA_MODE_SIMPLE = f"{CQ_DATA_MODE}.{Mode.SIMPLE}"
CQ_DATA_MODE_COMPLEX = f"{CQ_DATA_MODE}.{Mode.COMPLEX}"
