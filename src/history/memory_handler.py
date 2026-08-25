from .conversation import Conversation, Chat


class MemoryHandler:
    def __init__(self):
        self.conversation = Conversation()

    def create_chat(self, ticket_nr: int) -> Chat:
        return self.conversation.create_chat(ticket_nr)

    def get_chat(self, ticket_nr: int) -> Chat | None:
        for chat in self.conversation.chats:
            if chat.ticket_nr == ticket_nr:
                return chat

        return None

    def get_conversation(self) -> Conversation:
        return self.conversation