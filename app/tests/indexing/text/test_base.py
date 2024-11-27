import pytest

from langchain.schema import Document

from app.indexing.metadata import DocumentMetadata
from app.indexing.text.base import BaseTextIndexing
from app.tests.indexing.text.base import IndexingBase


class TestBaseTextIndexing(IndexingBase):

    @pytest.mark.parametrize('chunk_size,chunk_overlap,expected_chunks_num', [

        # Default values. Everthing should fit in a single chunk.
        (1_000, 200, 1),

        # Split the text into multiple chunks.
        (200, 50, 6),
    ])
    def test_split(
        self,
        text: str,
        metadata: DocumentMetadata,
        chunk_size: int,
        chunk_overlap: int,
        expected_chunks_num: int,
    ):

        # Run
        splits = BaseTextIndexing(chunk_size, chunk_overlap).split(text, metadata)
        
        # Validate
        assert len(splits) == expected_chunks_num
        assert [s.metadata for s in splits] == [metadata.to_dict()] * len(splits)
        assert all(s.page_content in text for s in splits)


    def test_store_existing_metadata_in_payload(self, text: str, metadata: DocumentMetadata):
        """The original metadata from a Document object should be stored in the payload."""
        
        # Setup
        text = [Document(page_content=text, metadata={
            'k1': 'A differnt value for k1',
            'k4': 'v4',
            'k5': 'v5',
            'source_name': 'A different source name',
        })]
        expected_metadata = metadata.to_dict()
        expected_metadata['payload']['k4'] = 'v4'
        expected_metadata['payload']['k5'] = 'v5'
        expected_metadata['payload']['source_name'] = 'A different source name'

        # Run
        splits = BaseTextIndexing().split(text, metadata)

        # Validate
        assert [s.metadata for s in splits] == [expected_metadata] * len(splits)
