from pathlib import Path

from .conversation import Conversation, Chat
from .repository import Repository


class MemoryHandler:
    def __init__(self, repository_path: str | Path):
        self.conversation = Conversation()
        self.repository = Repository(repository_path)

    # ------------------------------------------------------------------
    # Conversation
    # ------------------------------------------------------------------

    def create_chat(self, ticket_nr: int) -> Chat:
        return self.conversation.create_chat(ticket_nr)

    def get_chat(self, ticket_nr: int) -> Chat | None:
        for chat in self.conversation.chats:
            if chat.ticket_nr == ticket_nr:
                return chat

        return None

    # ------------------------------------------------------------------
    # Repository
    # ------------------------------------------------------------------

    def get_repository(self) -> Repository:
        return self.repository