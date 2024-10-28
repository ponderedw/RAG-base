import os

from langchain_openai import OpenAIEmbeddings as BaseOpenAIEmbeddings


class OpenAIEmbeddings(BaseOpenAIEmbeddings):
    """A wrapper for the `langchain_openai.OpenAIEmbeddings`.
    
    Adds specific configuration for the project.
    """

    def __init__(self, **kwargs):
        """Initialize the `OpenAIEmbeddings` with specific configuration."""
        
        default_kwargs = {
            'model': os.environ.get('EMBEDDING_MODEL', 'text-embedding-3-large'),
            'dimensions': 1024,
        }

        super().__init__(**(default_kwargs | kwargs))
