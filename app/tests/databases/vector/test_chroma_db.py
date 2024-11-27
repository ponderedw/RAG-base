import json

from app.databases.vector.chroma import Chroma
from app.tests.databases.vector.vector_db_tests_base import AllDocuments, BaseVectorDBTests


class TestChromaDB(BaseVectorDBTests):
    """Test the Chroma database."""
    VECTOR_DB_CLS = Chroma

    def get_all_documents(self) -> AllDocuments:
        res = self.VECTOR_DB_CLS().get()

        return AllDocuments(
            ids=res['ids'],
            metadatas=[{
                k: (v if k != 'payload' else json.loads(v))
                for k, v in m.items()
            } for m in res['metadatas']],
            texts=res['documents'],
        )
