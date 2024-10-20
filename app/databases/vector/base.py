import abc
import os

from langchain.schema import Document
from langchain_aws import BedrockEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class BaseVectorDatabase(abc.ABC):
    """Base class for vector databases."""

    def get_embedding_function(self) -> Embeddings:
        """Get the embedding function for the vector database."""

        # TODO: Add more options such as `Voyage`, `Gemini`.
        return BedrockEmbeddings(
            model_id=os.environ.get('EMBEDDING_MODEL', 'amazon.titan-embed-text-v2:0'),
            region_name='us-east-1',
        )
    
    async def split_and_store_text(
        self,
        text: str,
        metadata: dict,
        chunk_size: int = 1_000,
        chunk_overlap: int = 200,
    ) -> list[int]:
        """Store the embeddings for the given text in the vector database."""

        # Split the text into chunks.
        docs = [Document(page_content=text, metadata=metadata)]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        splits = text_splitter.split_documents(docs)

        # Store the embeddings for each chunk.
        return self.add_documents(documents=splits)
    
    @abc.abstractmethod
    async def delete_embeddings(self, source_id: str) -> dict:
        """Delete the embeddings for the given text from the vector database.
        
        :param source_id: The `source_id` metadata parameter to delete.
            This is not the same as the ID in the vector database, but rather the ID
            we use to identify the source, that the chunk of text came from.

        :return: A dictionary with the results of the deletion.
        """
        pass
