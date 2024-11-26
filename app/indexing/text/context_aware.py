from itertools import chain
from langchain.schema import Document
from langchain_core.language_models import BaseChatModel

from app.indexing.text.base import BaseTextIndexing
from app.models import ChatModel


def add_context_to_split(split: Document, context: str) -> Document:
    """Add the context to the split."""
    split.page_content = f'Context: {context}\n\nContent: {split.page_content}'
    return split


class ContextAwareIndexing(BaseTextIndexing):
    """Implements the context-aware text indexing strategy."""

    BASE_SUMMARIZE_PROMPT = """You are tasked with summarizing a document into 3 sentences max.
The summary should be concise and contain the main points of the document.
This is the document: """

    def __init__(
            self,
            *args,
            summarize_prompt: str = None,
            max_summary_tokens: int = 500,
            document_content_cutoff: int =  5_000,
            chat_model: BaseChatModel = None,
            **kwargs,
        ):
        super().__init__(*args, **kwargs)
        self.llm = chat_model or ChatModel(model_kwargs={
            'temperature': 0,
            'max_tokens': max_summary_tokens,
        })
        self.summarize_prompt = summarize_prompt or self.BASE_SUMMARIZE_PROMPT
        self.document_content_cutoff = document_content_cutoff

    def split(self, *args, **kwargs):
        """Split the text into chunks and return `Document` objects.
        
        This method also summarizes the document and adds the summary to the 
        beginning of each chunk, as context.
        """

        splits = iter(super().split(*args, **kwargs))

        # Summarize the document.
        document_content = ''
        splits_used = []
        while len(document_content) < self.document_content_cutoff:
            try:
                splits_used.append(next(splits))
                document_content += splits_used[-1].page_content
            except StopIteration:
                break

        document_content = document_content[:self.document_content_cutoff]
        res = self.llm.invoke(self.summarize_prompt + document_content)
        doc_summary = res.content

        # Add the context to each split.
        splits = (
            add_context_to_split(split, context=doc_summary)
            for split in chain.from_iterable([splits_used, splits])
        )

        return splits
