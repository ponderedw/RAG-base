from typing import Type

from app.tests.server.llm.history_tests_base import HistoryTests
from app.tests.server.llm.rag_tests_base import BaseRAGTests, NoDBSearchTests
from app.databases.vector.base import BaseVectorDatabase
from app.databases.vector.milvus import Milvus
from app.models.embeddings.openai_embeddings import OpenAIEmbeddings
from app.models.inference.openai_model import ChatOpenAI
from app.databases.vector.chroma import Chroma
from app.models.embeddings.bedrock_embeddings import BedrockEmbeddings
from app.models.inference.bedrock_model import ChatBedrock


# Note that we chose not to use a chartesian product of all the classes in the test.
# The main reason is the long time to run vs the lower value of testing every combination.
# That said, in real-world scenarios, you should use the combination of models and databases
# that you use in your product and make sure that they all work together.


class TestOpenAIWithMilvus(BaseRAGTests, HistoryTests):
    """Tests the OpenAI inference and embeddings models with Milvus."""

    INFERENCE_MODEL_NAME: str = 'gpt-3.5-turbo'
    INFERENCE_MODEL_CLASS = ChatOpenAI
    EMBEDDINGS_MODEL_CLASS = OpenAIEmbeddings
    VECTOR_DB_CLASS: Type[BaseVectorDatabase] = Milvus


class TestBedrockWithChroma(BaseRAGTests, NoDBSearchTests, HistoryTests):
    """Tests the Bedrock inference and embeddings models with Chroma."""

    INFERENCE_MODEL_NAME: str = 'anthropic.claude-3-5-sonnet-20240620-v1:0'
    INFERENCE_MODEL_CLASS = ChatBedrock
    EMBEDDINGS_MODEL_CLASS = BedrockEmbeddings
    VECTOR_DB_CLASS: Type[BaseVectorDatabase] = Chroma
