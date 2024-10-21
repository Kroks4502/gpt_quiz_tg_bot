from telethon import TelegramClient
from telethon.events.common import EventBuilder


class UserHandlerManager:
    def __init__(self):
        self._user_handlers = {}

    async def add(self, client: TelegramClient, peer, callback, event: EventBuilder):
        client.add_event_handler(callback, event)
        if not peer in self._user_handlers:
            self._user_handlers[peer] = [(callback, event)]
        else:
            self._user_handlers[peer].append((callback, event))
        await client.catch_up()

    async def remove_all(self, client: TelegramClient, user_id) -> int:
        handlers = self._user_handlers.pop(user_id, None)
        if not handlers:
            return 0

        for callback, event in handlers:
            client.remove_event_handler(callback, event)

        await client.catch_up()

        return len(handlers)

    def have_active_handler(self, user_id, callback = None, event: EventBuilder = None) -> bool:
        handlers = self._user_handlers.get(user_id, None)

        if not handlers:
            return False

        if not callback and not event:
            return True
        else:
            for cb, ev in handlers:
                if cb == callback and ev == event:
                    return True

        return False


handlers_manager: UserHandlerManager = UserHandlerManager()
