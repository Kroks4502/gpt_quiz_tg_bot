import logging

DT_FORMAT = "%Y.%m.%d_%H:%M:%S"
LOG_FORMAT = "%(name)-12s - %(levelname)-8s - %(message)s"

def configure_logging():
    logging.basicConfig(
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(logging.StreamHandler(),)
    )
    logging.getLogger("bot").setLevel(logging.DEBUG)
    logging.getLogger("gpt").setLevel(logging.DEBUG)
