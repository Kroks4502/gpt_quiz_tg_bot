from telethon import TelegramClient
from telethon.events.common import EventBuilder


class UserHandlerManager:
    def __init__(self):
        self._user_handlers = {}

    async def add(self, client: TelegramClient, user_id, callback, event: EventBuilder):
        client.add_event_handler(callback, event)

        if not user_id in self._user_handlers:
            self._user_handlers[user_id] = [(callback, event)]
        else:
            self._user_handlers[user_id].append((callback, event))

        await client.catch_up()

    async def remove_all(self, client: TelegramClient, user_id) -> int:
        handlers = self._user_handlers.pop(user_id, None)
        if not handlers:
            return 0

        for callback, event in handlers:
            i = len(client._event_builders)
            while i:
                i -= 1
                ev, cb = client._event_builders[i]
                if cb is callback and ev is event:
                    del client._event_builders[i]

        await client.catch_up()

        return len(handlers)

    def have_active_handler(self, user_id, callback=None, event: EventBuilder = None) -> bool:
        handlers = self._user_handlers.get(user_id, None)

        if not handlers:
            return False

        if not callback and not event:
            return True
        else:
            for cb, ev in handlers:
                if cb is callback and ev is event:
                    return True

        return False


handlers_manager: UserHandlerManager = UserHandlerManager()
