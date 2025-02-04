import os

from langchain_openai import OpenAIEmbeddings as BaseOpenAIEmbeddings


class OpenAIEmbeddings(BaseOpenAIEmbeddings):
    """A wrapper for the `langchain_openai.OpenAIEmbeddings`.
    
    Adds specific configuration for the project.
    """

    def __init__(self, **kwargs):
        """Initialize the `OpenAIEmbeddings` with specific configuration."""
        model_type_embedding, model_id_embedding = \
            os.environ.get('EMBEDDING_MODEL', 'openai:text-embedding-3-large').split(':', 1)
        default_kwargs = {
            'model': model_id_embedding,
            'dimensions': 1024,
        }

        super().__init__(**(default_kwargs | kwargs))
