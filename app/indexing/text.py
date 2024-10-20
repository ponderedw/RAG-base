from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


from source.app.indexing.metadata import DocumentMetadata


def split_and_store_text(text: str, metadata: DocumentMetadata, chunk_size: int = 1_000, chunk_overlap: int = 200) -> list[Document]:
    """Processes a blob of text in order to store it in a vector DB."""

    # Split the text into chunks.
    docs = [Document(page_content=text, metadata=metadata)]
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return text_splitter.split_documents(docs)
