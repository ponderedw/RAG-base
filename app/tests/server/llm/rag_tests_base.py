from unittest.mock import patch

from app.server.llm import LLMAgent, LLMEventType
from app.tests.server.llm.base import BaseTestChatAgent


class BaseRAGTests(BaseTestChatAgent):
    """Implements basic tests for RAG agents."""

    async def test_stream_events(self, chat_session: dict):
        """Test the `stream_events` method.
        
        Check that we find information in the vector database, retrieve it and get a proper
        response from the LLM.
        """

        # Setup
        agent = LLMAgent()
        message = 'What do we know about Hipposys? If you cannot find it, please write "00--NO_INFO--00".'
        chat_messages = []

        async with agent:

            # Run
            chat_messages = [
                msg
                async for msg in agent.astream_events(message, chat_session)
            ]

            # Validate - Sanity, make sure that we were using the correct models and DB.
            agent_tools = agent._agent.get_graph().nodes['tools']
            retriever_tool = agent_tools.data.tools_by_name[agent.retriever_tool_name]
            retriever_tool_tags = retriever_tool.func.keywords['retriever'].tags
            assert self.EMBEDDINGS_MODEL_CLASS.__name__ in retriever_tool_tags
            assert self.VECTOR_DB_CLASS.__name__ in retriever_tool_tags
            assert isinstance(agent._llm, self.INFERENCE_MODEL_CLASS)

        # Validate
        results = ''.join(msg.content for msg in chat_messages)
        assert 'data and ai engineering consultancy' in results.lower()
        assert 'About Hipposys' in results
        assert '00--NO_INFO--00' not in results
    
    async def test_stream_events_no_info(self, chat_session: dict):
        """Test the `stream_events` method when the information is not found.
        
        The question asked is about a topic that is not in the database. The LLM
        responds accordingly.
        """

        # Setup
        agent = LLMAgent()
        message = 'What do we know about Project XYZ? If you cannot find it, please write "00--NO_INFO--00".'
        chat_messages = []

        async with agent:

            # Run
            chat_messages = [
                msg
                async for msg in agent.astream_events(message, chat_session)
            ]

        # Validate
        results = ''.join(msg.content for msg in chat_messages)
        assert '00--NO_INFO--00' in results

    async def test_stream_events_vector_db_empty(self, chat_session: dict):
        """Test the `stream_events` method when the vector database is empty."""

        # Setup
        agent = LLMAgent()
        message = 'What do we know about Hipposys? If you cannot find it, please write "00--NO_INFO--00".'
        chat_messages = []

        # Setup - use an empty collection.
        with patch.dict('os.environ', {'DEFAULT_VECTOR_DB_COLLECTION_NAME': 'empty_collection_123'}):
            async with agent:

                # Run
                chat_messages = [
                    msg
                    async for msg in agent.astream_events(message, chat_session)
                ]

        # Validate
        results = ''.join(msg.content for msg in chat_messages)
        assert '00--NO_INFO--00' in results 


class NoDBSearchTests(BaseTestChatAgent):
    """Implements tests for the case where there is no need to access the DB for an answer.
    
    Note that depending on the model and the prompt, some agents may always try to access
    the DB, even for questions that require only general knowledge.
    """

    async def test_no_db_search(self, chat_session: dict):
        """Test the `stream_events` method when there is no need to search the database.

        The question asked is about a topic that is a general know-how.
        """
    
        # Setup
        agent = LLMAgent()
        message = 'How much is 4 x 212?'
        chat_messages = []

        async with agent:

            # Run
            chat_messages = [
                msg
                async for msg in agent.astream_events(message, chat_session)
            ]

        # Validate
        results = ''.join(msg.content for msg in chat_messages)
        assert '848' in results

        # Validate - Didn't search the DB.
        assert {msg.type for msg in chat_messages} == {LLMEventType.CHAT_CHUNK, LLMEventType.DONE}
