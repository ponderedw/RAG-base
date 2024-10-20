
from pathlib import Path
from xml.dom.minidom import Document

from langchain_text_splitters import RecursiveCharacterTextSplitter

from source.app.indexing.metadata import DocumentMetadata


def split_and_store_docx(file_path: str | Path, metadata: DocumentMetadata, chunk_size: int = 1_000, chunk_overlap: int = 200) -> list[Document]:

    loader = Docx2txtLoader(file_path)
    docs = loader.load()

    for doc in docs:
            doc.metadata = doc.metadata | {
                'source_id': file_rec['URL'],
                'source_name': file_rec['Name'],
                'modified_at': file_rec['Modified Time'],
            }

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
