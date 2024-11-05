import json
import uuid
import pytest

from pathlib import Path
from typing import AsyncGenerator, Generator, Type
from unittest.mock import patch

from app.databases.vector.base import BaseVectorDatabase


class BaseTestChatAgent:
    """Base class for testing chat agents.
    
    Implements general setup needed for testing the chat agents.

    To use this class, you'll need to configure the following class attributes:
    - `INFERENCE_MODEL_NAME`: The name of the inference model.
    - `INFERENCE_MODEL_CLASS`: The class of the inference model.
    - `EMBEDDINGS_MODEL_CLASS`: The class of the embeddings model.
    - `VECTOR_DB_CLASS`: The class of the vector database.
    """

    FIXTURES_PATH = Path(__file__).parent / 'fixtures.jsonl'
    
    INFERENCE_MODEL_NAME: str = None
    INFERENCE_MODEL_CLASS = None
    EMBEDDINGS_MODEL_CLASS = None
    VECTOR_DB_CLASS: Type[BaseVectorDatabase] = None

    @pytest.fixture
    def chat_session(self, session_id: str = None) -> dict:
        """Return a chat session dictionary."""
        return {'configurable': {
            'thread_id': session_id or f'test_session_{uuid.uuid4()}',
        }}

    @pytest.fixture(scope='class')
    def collection_name(self) -> Generator[str, None, None]:
        """Return the collection name for the test."""
        return f'test_collection_{uuid.uuid4()}'.replace('-', '')
    
    @pytest.fixture(scope='class', autouse=True)
    def setup_environment(self, collection_name: str) -> Generator:
        """Set up the ENV and the classes used for inference, embeddings, etc."""

        new_env = {
            'LLM_MODEL_ID': self.INFERENCE_MODEL_NAME,
            'DEFAULT_VECTOR_DB_COLLECTION_NAME': collection_name,
        }
        with \
                patch('app.server.llm.VectorDB', self.VECTOR_DB_CLASS), \
                patch('app.databases.vector.base.EmbeddingsModel', self.EMBEDDINGS_MODEL_CLASS), \
                patch.dict('os.environ', new_env), \
                patch('app.server.llm.ChatModel', self.INFERENCE_MODEL_CLASS):
            
            yield

    @pytest.fixture(scope='class', autouse=True)
    async def setup_vector_db(self, collection_name: str) -> AsyncGenerator[BaseVectorDatabase, None]:
        """Set up the vector database with test data."""

        # Setup
        vector_db = self.VECTOR_DB_CLASS(collection_name=collection_name)
        with open(self.FIXTURES_PATH, 'r') as fixtures_fd:
            for line in fixtures_fd:

                # Store the data from the JSON snippet in the DB.
                data = json.loads(line)
                await vector_db.split_and_store_text(
                    data['text'],
                    # Metadata is all the fields in the JSON except for 'text'.
                    metadata={k: v for k, v in data.items() if k != 'text'},
                )

        try:
            # Run
            yield vector_db
        except Exception:
            # Cleanup
            await vector_db.drop_collection(collection_name)
            raise

