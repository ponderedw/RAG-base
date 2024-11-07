import chromadb
import os

from langchain_chroma import Chroma as LangChroma
from urllib.parse import urlparse

from app.databases.vector.base import BaseVectorDatabase


class Chroma(LangChroma, BaseVectorDatabase):

    FILE_SYSTEM_SCHEMA = 'fs://'
    SERVER_SCHEMA = 'http://'
    SERVER_SECURE_SCHEMA = 'https://'

    def get_chroma_http_client(self, uri: str) -> chromadb.HttpClient:
        """Parse `uri` and return an HTTP client object for the Chroma database."""
        
        # Parse the URI.
        parsed_uri = urlparse(uri)
        host = parsed_uri.hostname
        port = parsed_uri.port
        username = parsed_uri.username
        password = parsed_uri.password
    
        # Construct and return the client object.
        print(f'Connecting to Chroma database at {host}:{port}')
        return chromadb.HttpClient(
            host=host,
            port=port,
            settings=chromadb.config.Settings(
                chroma_client_auth_provider='chromadb.auth.basic_authn.BasicAuthClientProvider',
                chroma_client_auth_credentials=f'{username}:{password}',
            ),
        )
    
    def __init__(self, collection_name: str = None, **kwargs):
        """Initialize a Chroma database client.
        
        The `CHROMA_DB_URI` environment variable should be set to the URI of the Chroma database.

        Supported URI schemas:
        - `http://`: Connect to a remote Chroma database.
        - `fs://`: Connect to a local file system database.
        """

        self.collection_name = collection_name or self.get_default_collection_name()
        self.client = None

        # Parse the connection URI and set the HTTP client or local FS directory, accordingly.
        chroma_db_uri = os.environ.get('CHROMA_DB_URI', 'http://localhost:6000')
        if chroma_db_uri.startswith(self.SERVER_SCHEMA) or chroma_db_uri.startswith(self.SERVER_SECURE_SCHEMA):
            # HTTP client.
            self.client = self.get_chroma_http_client(chroma_db_uri)
        elif chroma_db_uri.startswith(self.FILE_SYSTEM_SCHEMA):
            # Local file system.
            self.client = chromadb.Client(chromadb.config.Settings(
                is_persistent=True,
                persist_directory=chroma_db_uri[len(self.FILE_SYSTEM_SCHEMA):],
            ))
        else:
            # Invalid schema.
            raise ValueError(f'Invalid CHROMA_DB_URI Schema: {chroma_db_uri}')

        kwargs['client'] = self.client
        default_kwargs = {
            'embedding_function': self.get_embedding_function(),
        }

        super().__init__(
            collection_name=self.collection_name,
            **(default_kwargs | kwargs),
        )

    async def delete_embeddings(self, source_id: str) -> dict:
        """Delete the embeddings for the given text from the Chroma database."""
        
        # Must use the "low-level" API to delete using a condition (and not by ID).
        collection = self.client.get_collection(self.collection_name)
        collection.delete(where={'source_id': source_id})

        # Chroma DB doesn't provide statistics on deletion.
        return {
            'success': True,
            'error_count': 0,
        }

    async def drop_collection(self, collection_name: str, ignore_non_exist: bool = False) -> None:
        """Drop the collection from the Chroma database."""
        self.client.delete_collection(collection_name)
