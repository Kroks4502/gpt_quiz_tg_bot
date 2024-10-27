from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .history import AssistantHistory
from .user import User, UserTopic
