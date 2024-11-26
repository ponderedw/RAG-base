import abc
import pytest
import uuid

from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import AsyncGenerator, Type
from unittest.mock import patch

from app.databases.vector.base import BaseVectorDatabase
from app.indexing.metadata import DocumentMetadata
from app.indexing.text.base import BaseTextIndexing
from app.tests.test_utils.string_utils import regularize_spaces


InsertTestParameters = namedtuple('InsertTestParameters', ['text', 'metadata', 'expected_entries'])


@dataclass
class AllDocuments:
    ids: list[str]
    metadatas: list[dict]
    texts: list[str]


class BaseVectorDBTests(abc.ABC):
    """Base class for testing vector databases.
    
    Contains common tests for vector databases + common setup.

    Inheriting classes should set the following:
    - `VECTOR_DB_CLS`: The class of the vector database to test.
    - `get_all_documents`: A method to get all documents from the vector database 
        in a predefined format (`AllDocuments`).
    """

    VECTOR_DB_CLS: Type[BaseVectorDatabase] = None

    @abc.abstractmethod
    def get_all_documents(self) -> AllDocuments:
        """Abstract method to get all documents from the vector database in a predefined format."""
        pass

    async def create_collection_if_not_exists(
        self,
        vector_db: BaseVectorDatabase,
        entry: InsertTestParameters,
    ) -> None:
        """Create the collection if it does not exist.
        
        Not needed by default. Override if necessary.
        """
        pass

    @pytest.fixture
    def entries(self) -> list[DocumentMetadata]:
        """Return a list of metadata for the test."""
        metadatas = [
            DocumentMetadata(source_id='19291', source_name='test1', modified_at=datetime(2021, 1, 1)),
            DocumentMetadata(source_id='223344', source_name='test2', modified_at=datetime(2021, 2, 2)),
            DocumentMetadata(source_id='123456', source_name='test3', modified_at=datetime(2021, 3, 3)),
            DocumentMetadata(source_id='987654', source_name='test4', modified_at=datetime(2021, 4, 4)),
        ]
        return [
            InsertTestParameters('This is a test.', metadatas[0], 0),
            InsertTestParameters('The quick brown fox jumps over the lazy dog.', metadatas[1], 0),
            InsertTestParameters('lorum ipsum dolor sit amet.', metadatas[2], 0),
            InsertTestParameters('Attention is all you need', metadatas[3], 0),
        ]

    @pytest.fixture(autouse=True)
    async def collection_name(self) -> AsyncGenerator[str, None]:
        """Return the collection name for the test."""

        # Setup
        collection_name = f'test_collection_{uuid.uuid4()}'.replace('-', '')
        with patch.dict('os.environ', {'DEFAULT_VECTOR_DB_COLLECTION_NAME': collection_name}):

            try:
                # Run
                yield collection_name
            finally:
                # Cleanup
                await self.VECTOR_DB_CLS().drop_collection(collection_name, ignore_non_exist=True)

    @pytest.mark.parametrize('text,metadata,expected_entries', [
        # Simple case of short text.
        InsertTestParameters(
            text='This is a simple text to test the vector database.',
            metadata=DocumentMetadata(source_id=1, source_name='test1', modified_at=datetime(2021, 1, 1)),
            expected_entries=1,
        ),

        # Longer text that gets split into multiple entries.
        InsertTestParameters(
            text="""
            This is a longer text to test the vector database. It has multiple lines. Each line
            contains different text about a different subject.

            For example, here we talk about the weather. It is sunny today. The temperature is
            25 degrees Celsius. The sky is clear.

            Last Paragraph. The quick brown fox jumps over the lazy dog. The end.
            """,
            metadata=DocumentMetadata(source_id=2, source_name='test2', modified_at=datetime(2021, 2, 2)),
            expected_entries=3,
        ),
    ])
    async def test_vector_db_insert(self, collection_name: str, text: str, metadata: dict, expected_entries: int):
        """Test the insertion of text into the vector database."""

        # Setup
        vector_db = self.VECTOR_DB_CLS(split_strategy=BaseTextIndexing(chunk_size=200, chunk_overlap=20))
        epsilon = 0.001
        chunks_separator = '\n\n'

        # Run
        ids = await vector_db.split_and_store_text(text, metadata)

        # Validate - the number of entries is as expected.
        assert len(ids) == expected_entries

        # Validate - regular `get` returns only the documents we entered into the DB.
        res = self.get_all_documents()
        assert res.ids == ids
        assert res.metadatas == [metadata.to_dict()] * len(ids)
        assert regularize_spaces(' '.join(res.texts)) == regularize_spaces(text)

        # Validate - Similarity search with `text` returns the same document with perfect similarity score.
        search_term = text.split(chunks_separator)[0].strip()
        (doc, score), *_ = vector_db.similarity_search_with_score(search_term, 1)
        assert 0 - epsilon <= score <= 0 + epsilon  # Yes, the `0` is intentional, although unnecessary.
        assert doc.page_content == search_term

        # Validate - Similarity search with unrelated search term still returns document
        # but with a lower similarity score.
        search_term = '!*@(#--UNR3L4T3D STUFF--*#*#'
        (doc, score), *_ = vector_db.similarity_search_with_score(search_term, 1)
        assert score > epsilon
        assert doc.page_content != search_term
        assert doc.page_content in text

    @pytest.mark.parametrize('number_of_entries,delete_idx', [

        # Delete an entry from the middle of the list.
        (4, 1),

        # Delete the only entry in the DB.
        (1, 0),

        # Delete a non-existent entry.
        (0, 1),
    ])
    async def test_vector_db_delete(self, entries: list[InsertTestParameters], number_of_entries: int, delete_idx: int):
        """Test the deletion of entries from the vector database."""

        # Setup
        ids = []
        vector_db = self.VECTOR_DB_CLS()
        await self.create_collection_if_not_exists(vector_db, entries[0])
        
        # Setup - Insert the entries.
        for entry in entries[:number_of_entries]:
            ids += await vector_db.split_and_store_text(entry.text, entry.metadata)
                
        # Run
        entry_to_delete = entries[delete_idx]
        await vector_db.delete_embeddings(entry_to_delete.metadata.source_id)

        # Validate
        db_content = self.get_all_documents()
        assert entry_to_delete.metadata not in db_content.metadatas
        assert db_content.ids == ids[:delete_idx] + ids[delete_idx + 1:]

    async def test_vector_db_drop_collection(self, entries: list[InsertTestParameters], collection_name: str):
        """Test the dropping of a collection from the vector database."""
        
        # Setup
        vector_db = self.VECTOR_DB_CLS()
        
        # Setup - Insert the entries.
        for entry in entries:
            await vector_db.split_and_store_text(entry.text, entry.metadata)

        # Run
        await vector_db.drop_collection(collection_name)

        # Validate - The collection is empty.
        assert self.get_all_documents().ids == []
    
    async def test_embedding_function(self):
        """`get_embedding_function` returns an instance of `EmbeddingsModel`."""
        
        # Setup
        org_embedding_function = self.VECTOR_DB_CLS().get_embedding_function()
        with patch('app.databases.vector.base.EmbeddingsModel') as EmbeddingsModelClassMock:
            EmbeddingsModelClassMock.return_value.embed_documents.return_value = \
                org_embedding_function.embed_documents(['blah blah'])
            
            # Run
            vector_db = self.VECTOR_DB_CLS()
            
            # Validate - EmbeddingsModelClassMock was called during `__init__`.
            EmbeddingsModelClassMock.assert_called_once()

            # Validate - `get_embedding_function` returns an instance of `EmbeddingsModelClassMock`.
            assert vector_db.get_embedding_function() == EmbeddingsModelClassMock.return_value

            # with patch.object(vector_db, 'add_documents'):
            # Run - `split_and_store_text` calls `EmbeddingsModelClassMock` to get embeddings.
            metadata = DocumentMetadata(source_id='1', source_name='test', modified_at=datetime(2021, 1, 1))
            await vector_db.split_and_store_text('This is a test u4i2o1.', metadata)

        # Validate - `EmbeddingsModelClassMock` was called during `split_and_store_text`.
        EmbeddingsModelClassMock.return_value.embed_documents.assert_called_once_with(['This is a test u4i2o1.'])

    @pytest.mark.skip('Going to move this functionality elsewhere, so skipping for now.')
    async def test_change_split_parameters(self):
        assert False
