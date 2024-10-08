import os

from pathlib import Path

from langchain_aws import BedrockEmbeddings
from langchain_milvus.vectorstores import Milvus as LangMilvus
from langchain_core.embeddings import Embeddings
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class Milvus(LangMilvus):
    """A wrapper for a Milvus database for the project."""

    @staticmethod
    def get_local_connection_args() -> dict:
        """Get the URI for the Milvus database.
        
        The easiest way is to use Milvus Lite where everything is stored in a local file.
        If you have a Milvus server you can use the server URI such as 'http://localhost:19530'.
        """        
        
        return {
            'uri': os.environ.get('MILVUS_SERVER_URI', 'http://localhost:19530'),
        }
        # return {'uri': str(Path(__file__).parent.parent.parent / 'milvus' / 'milvus_demo.db')}
    
    def get_embedding_function(self) -> Embeddings:
        """Get the embedding function for the Milvus database."""

        return BedrockEmbeddings(
            model_id='amazon.titan-embed-text-v2:0',  # Consider using `Voyage` or `Gemini`.
            region_name='us-east-1',
        )

    def __init__(self, collection_name: str = 'MyRAGApp', **kwargs):
        """Initialize the Milvus database for the project."""

        default_kwargs = {
            'embedding_function': self.get_embedding_function(),
            'connection_args': self.get_local_connection_args(),
            'consistency_level': 'Strong',
            'auto_id': True
        }

        super().__init__(
            collection_name=collection_name,
            **(default_kwargs | kwargs),
        )

    async def split_and_store_text(self, text: str, metadata: dict, chunk_size=1000, chunk_overlap=200) -> list[int]:
        """Store the embeddings for the given text in the Milvus database."""

        # Split the text into chunks.
        docs = [Document(page_content=text, metadata=metadata)]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        splits = text_splitter.split_documents(docs)

        # Store the embeddings for each chunk.
        return self.add_documents(documents=splits)

    async def delete_embeddings(self, source_id: str) -> str:
        """Delete the embeddings for the given text from the Milvus database."""
        
        # The loop is needed because the deletion doesn't always happen and
        # even if we wait a while, we don't see it in the database.
        # TODO: Consider trying a different consistency level. Or using `.release`, `.flush`, etc.
        res = []
        for i in range(10):
            res.append(str(self.delete(expr=f'source_id == "{source_id}"')))
            if 'delete count: 0' in res[-1]:
                break

        return '\n'.join(res)
