from app.tests.server.llm.base import BaseTestChatAgent
from app.server.llm import ChatMessage, LLMAgent


class HistoryTests(BaseTestChatAgent):
    """Tests the chat history functionality."""

    async def test_chat_history(self, chat_session: dict):
        """Correctly returns the chat history on request."""

        # Setup
        agent = LLMAgent()
        message_1 = 'Hello, my name is Dave and I work at Ponder.'
        message_2 = "Can you repeat what I've just told you?"

        async with agent:

            # Setup - add some history
            async for msg in agent.astream_events(message_1, chat_session):
                pass
            async for msg in agent.astream_events(message_2, chat_session):
                pass

            # Run
            chat_history = await agent.aget_history(chat_session)

        # Validate - Human messages.
        assert {k: v for k, v in chat_history[0].items() if k in ('sender', 'content')} == {
            'sender': ChatMessage.Sender.HUMAN.value,
            'content': message_1,
        }
        assert {k: v for k, v in chat_history[2].items() if k in ('sender', 'content')} == {
            'sender': ChatMessage.Sender.HUMAN.value,
            'content': message_2,
        }

        # Validate - The rest of the messages are not from the human.
        assert {msg['sender'] for i, msg in enumerate(chat_history) if i not in (0, 2)} <= {
            ChatMessage.Sender.AI.value,
            ChatMessage.Sender.TOOL.value,
        }

    async def test_chat_history_empty(self, chat_session: dict):
        """Returns an empty chat history if there was no conversation."""

        # Setup
        agent = LLMAgent()

        async with agent:
    
            # Run
            chat_history = await agent.aget_history(chat_session)

        # Validate
        assert chat_history == []
