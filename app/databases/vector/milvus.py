import os

from langchain_milvus.vectorstores import Milvus as LangMilvus

from app.databases.vector.base import BaseVectorDatabase


class Milvus(BaseVectorDatabase, LangMilvus):
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
    
    def __init__(self, **kwargs):
        """Initialize the Milvus database for the project."""

        default_kwargs = {
            'connection_args': self.get_local_connection_args(),
            'consistency_level': 'Strong',
            'auto_id': True,
        }
        super().__init__(**(default_kwargs | kwargs))

    async def delete_embeddings(self, source_id: str, should_compact: bool = False) -> dict:
        """Delete the embeddings for the given text from the Milvus database.
        
        :param source_id: The ID of the text to delete.
        :param should_compact: Whether to compact the database after deletion. If not compacted, data
            may still be present in the database, until Milvus decides to compact it.
            That said, compacting on every deletion may result in slower performance.
        """
        
        res = self.delete(expr=f'source_id == "{source_id}"')
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
    
    async def drop_collection(self, collection_name: str, ignore_non_exist: bool = False) -> None:
        """Drop the collection from the Milvus database."""

        assert collection_name == self.collection_name, 'Can drop only the current collection.'

        if ignore_non_exist and self.col is None:
            return

        self.col.drop()
