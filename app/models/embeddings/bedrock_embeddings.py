import os

from langchain_aws import BedrockEmbeddings as BaseBedrockEmbeddings
from langchain_ollama import OllamaEmbeddings


class BedrockEmbeddings(BaseBedrockEmbeddings):
    """A wrapper for the langchain_aws.BedrockEmbeddings.
    
    Adds specific configuration for the project.
    """

    def __init__(self, **kwargs):
        """Initialize the BedrockEmbeddings for the project."""
        
        default_kwargs = {
            'model_id': os.environ.get('EMBEDDING_MODEL', 'amazon.titan-embed-text-v2:0'),
            'region_name': os.environ.get('AWS_REGION', 'us-east-1'),
        }

        super().__init__(**(default_kwargs | kwargs))


class CustomOllamaEmbeddings(OllamaEmbeddings):
    """A wrapper for the langchain_aws.BedrockEmbeddings.

    Adds specific configuration for the project.
    """

    def __init__(self, **kwargs):
        """Initialize the BedrockEmbeddings for the project."""

        default_kwargs = {
            'model': os.environ.get('LOCAL_EMBEDDING_MODEL', None),
            'base_url': 'http://local_model:11434'
        }

        super().__init__(**(default_kwargs | kwargs))
