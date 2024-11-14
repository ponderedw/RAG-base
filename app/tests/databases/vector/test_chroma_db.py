from app.databases.vector.chroma import Chroma
from app.tests.databases.vector.vector_db_tests_base import AllDocuments, BaseVectorDBTests


class TestChromaDB(BaseVectorDBTests):
    """Test the Chroma database."""
    VECTOR_DB_CLS = Chroma

    def get_all_documents(self) -> AllDocuments:
        res = self.VECTOR_DB_CLS().get()

        return AllDocuments(
            ids=res['ids'],
            metadatas=res['metadatas'],
            texts=res['documents'],
        )
