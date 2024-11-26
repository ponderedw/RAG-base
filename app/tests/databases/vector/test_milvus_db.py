import pytest

from langchain.schema import Document

from app.databases.vector.base import BaseVectorDatabase
from app.databases.vector.milvus import Milvus
from app.tests.databases.vector.vector_db_tests_base import (
    AllDocuments,
    BaseVectorDBTests,
    InsertTestParameters,
)


class TestMilvusDB(BaseVectorDBTests):
    """Test the Milvus database."""
    VECTOR_DB_CLS = Milvus

    def get_all_documents(self) -> AllDocuments:

        # Search is good enough because the total number of documents
        # is less than `k`.
        res: list[Document] = self.VECTOR_DB_CLS().search('', 'similarity', k=100)

        # But we need to sort by `pk` to ensure the order is consistent.
        res.sort(key=lambda doc: doc.metadata['pk'])

        return AllDocuments(
            ids=[doc.metadata['pk'] for doc in res],
            metadatas=[
                {k: v for k, v in doc.metadata.items() if k != 'pk'}
                for doc in res
            ],
            texts=[doc.page_content for doc in res],
        )

    async def create_collection_if_not_exists(
        self,
        vector_db: BaseVectorDatabase,
        entry: InsertTestParameters,
    ) -> None:
        """Create the collection if it does not exist."""

        # Add and delete a document to make sure the collection exists.
        await vector_db.split_and_store_text(entry.text, entry.metadata)
        await vector_db.delete_embeddings(entry.metadata.source_id)

    async def test_delete_not_current_collection(self, collection_name: str):
        """Should fail if trying to delete a collection that is not the current one."""

        # Setup
        vector_db = self.VECTOR_DB_CLS()

        # Run + Validate
        with pytest.raises(AssertionError) as exc_ctx:
            await vector_db.drop_collection(collection_name + '111')

        assert str(exc_ctx.value) == 'Can drop only the current collection.'
