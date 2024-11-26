from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Iterable

from app.indexing.metadata import DocumentMetadata


def enhance_metadata(doc: Document, metadata_dict: dict) -> Document:
    """Enhance the document metadata with the given metadata dictionary.
    
    Operation is done in-place.

    :return: The document with the enhanced metadata.
    """
    doc.metadata = metadata_dict | {
        'payload': doc.metadata | metadata_dict.get('payload', {}),
    }
    return doc


class BaseTextIndexing:
    """Implements the base strategy for text splitting and indexing."""

    def __init__(self, chunk_size: int = 1_000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str | Iterable[Document], metadata: DocumentMetadata) -> Iterable[Document]:
        """Split the text into chunks and return `Document` objects."""

        docs = [Document(page_content=text)] if isinstance(text, str) else text
        metadata_dict = metadata.to_dict()
        
        # Replace the original metadata with `metadata` and add the original metadata to the new metadata payload.
        docs = (enhance_metadata(doc, metadata_dict) for doc in docs)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        splits = text_splitter.split_documents(docs)

        return splits
