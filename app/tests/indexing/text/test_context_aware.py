import pytest

from typing import Iterable
from unittest.mock import MagicMock, patch

from app.indexing.metadata import DocumentMetadata
from app.indexing.text.context_aware import ContextAwareIndexing
from app.tests.indexing.text.base import IndexingBase
    

class TestContextAwareIndexing(IndexingBase):

    @staticmethod
    def split_context_content(text: str) -> tuple[str, str]:
        """Split the text into context and content."""
        context, content = text.split('Content: ')
        return context[len('Context: '):].strip(), content[len('Content: '):].strip()

    @staticmethod
    def extract_context(split: str) -> str:
        """Extract the context from the split."""
        return TestContextAwareIndexing.split_context_content(split)[0]
    
    @staticmethod
    def extract_content(split: str) -> str:
        """Extract the content from the split."""
        return TestContextAwareIndexing.split_context_content(split)[1]

    @pytest.mark.parametrize('chunk_size,chunk_overlap,expected_chunks_num', [

        # Default values. Everthing should fit in a single chunk.
        (1_000, 200, 1),

        # Split the text into multiple chunks.
        (200, 50, 6),
    ])
    def test_adds_summary_to_each_chunk(
        self,
        text: str,
        metadata: DocumentMetadata,
        chunk_size: int,
        chunk_overlap: int,
        expected_chunks_num: int,
    ):
        """Test that the summary is added to each chunk as context."""

        # Setup
        indexer = ContextAwareIndexing(
            chunk_overlap=chunk_overlap,
            chunk_size=chunk_size,
        )

        expected_summary = 'This is the summary of the document. It contains lorem ipsum and the brown fox.'
        with patch.object(indexer, 'llm') as mock_llm:
            mock_llm.invoke.return_value.content = expected_summary

            # Run
            splits = indexer.split(text, metadata)

        # Validate - splits is an iterator, not a list
        assert isinstance(splits, Iterable) and not isinstance(splits, list)
        
        # Validate - splits contain the expected number of chunks, the text, and the metadata
        splits = list(splits)
        assert len(splits) == expected_chunks_num
        assert [s.metadata for s in splits] == [metadata.to_dict()] * len(splits)
        assert all(self.extract_content(s.page_content) in text for s in splits)

        # Validate - each split contains the summary as context
        assert all(self.extract_context(s.page_content) == expected_summary for s in splits)

    @pytest.mark.parametrize('cutoff', [
        # All document
        5_000,
        
        # Part of document
        500,
        40,
    ])
    def test_document_content_cutoff(self, text: str, metadata: DocumentMetadata, cutoff: int):
        """Runs summary only on the first `cutoff` characters."""

        # Setup
        indexer = ContextAwareIndexing(document_content_cutoff=cutoff)
        with patch.object(indexer, 'llm') as mock_llm:
            mock_llm.invoke.return_value.content = 'summary'

            # Run
            indexer.split(text, metadata)

        # Validate
        mock_llm.invoke.assert_called_once_with(indexer.BASE_SUMMARIZE_PROMPT + text[:cutoff])

    def test_summarize_prompt(self, text: str, metadata: DocumentMetadata):
        """Test that the summarize prompt is fed to the LLM to produce the summary."""

        # Setup
        expected_prompt = 'My very special instrcutions to the LLM =)'
        indexer = ContextAwareIndexing(summarize_prompt=expected_prompt)
        with patch.object(indexer, 'llm') as mock_llm:
            mock_llm.invoke.return_value.content = 'summary'

            # Run
            indexer.split(text, metadata)

        # Validate
        mock_llm.invoke.assert_called_once_with(expected_prompt + text)

    @pytest.mark.parametrize('max_summary_tokens', [500, 50, 10])
    def test_max_summary_tokens(self, max_summary_tokens: int):
        """Test `max_summary_tokens` is fed to the LLM."""
        
        # Setup + Run
        indexer = ContextAwareIndexing(max_summary_tokens=max_summary_tokens)
        
        # Validate
        assert indexer.llm.model_kwargs['max_tokens'] == max_summary_tokens

    def test_chat_model(self, text: str, metadata: DocumentMetadata):
        """Test that the chat model is used to summarize the document."""
        
        # Setup
        chat_model = MagicMock()

        # Run
        indexer = ContextAwareIndexing(chat_model=chat_model)
        indexer.split(text, metadata)
        
        # Validate
        chat_model.invoke.assert_called_once_with(indexer.BASE_SUMMARIZE_PROMPT + text)

