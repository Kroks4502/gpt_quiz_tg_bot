from functools import wraps
from typing import Callable

from db.manager import sessionmanager


def use_async_session_context(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with sessionmanager.session() as session:
            return await func(*args, session=session, **kwargs)

    return wrapper
