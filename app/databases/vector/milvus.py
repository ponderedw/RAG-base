import os

from langchain_milvus.vectorstores import Milvus as LangMilvus

from app.databases.vector.base import BaseVectorDatabase


class Milvus(LangMilvus, BaseVectorDatabase):
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
    
    def __init__(self, collection_name: str = None, **kwargs):
        """Initialize the Milvus database for the project."""

        collection_name = collection_name or self.get_default_collection_name()
        default_kwargs = {
            'embedding_function': self.get_embedding_function(),
            'connection_args': self.get_local_connection_args(),
            'consistency_level': 'Strong',
            'auto_id': True,
        }

        super().__init__(
            collection_name=collection_name,
            **(default_kwargs | kwargs),
        )

    async def delete_embeddings(self, source_id: str, should_compact: bool = False) -> dict:
        """Delete the embeddings for the given text from the Milvus database.
        
        :param source_id: The ID of the text to delete.
        :param should_compact: Whether to compact the database after deletion. If not compacted, data
            may still be present in the database, until Milvus decides to compact it.
            That said, compacting on every deletion may result in slower performance.
        """
        
        res = self.delete(expr=f'source_id == "{source_id}"', consistency_level='Strong')
        if should_compact:
            self.col.compact()

        return {
            'insert_count': int(res.insert_count),
            'delete_count': int(res.delete_count),
            'upsert_count': int(res.upsert_count),
            'timestamp': float(res.timestamp),
            'success_count': int(res.succ_count),
            'error_count': int(res.err_count),
            'error_index': str(res.err_index),
        }
    
    async def drop_collection(self, collection_name: str) -> None:
        """Drop the collection from the Milvus database."""
        self.col.drop_collection(collection_name)
