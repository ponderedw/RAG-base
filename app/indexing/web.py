from langchain.schema import Document


def split_and_store_web(url: str, metadata: dict, chunk_size=1000, chunk_overlap=200) -> list[int]:
        """Store the embeddings for the given text in the Milvus database."""

        # Split the text into chunks.
        docs = [Document(page_content=text, metadata=metadata)]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        splits = text_splitter.split_documents(docs)

        # Store the embeddings for each chunk.
        return self.add_documents(documents=splits)
