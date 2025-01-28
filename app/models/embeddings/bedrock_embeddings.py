import os

from langchain_aws import BedrockEmbeddings as BaseBedrockEmbeddings


class BedrockEmbeddings(BaseBedrockEmbeddings):
    """A wrapper for the langchain_aws.BedrockEmbeddings.
    
    Adds specific configuration for the project.
    """
    def __init__(self, **kwargs):
        """Initialize the BedrockEmbeddings for the project."""
        model_type_embedding, model_id_embedding = \
            os.environ.get('EMBEDDING_MODEL', 'bedrock:amazon.titan-embed-text-v2:0').split(':', 1)
        default_kwargs = {
            'model_id': model_id_embedding,
            'region_name': os.environ.get('AWS_REGION', 'us-east-1'),
        }

        super().__init__(**(default_kwargs | kwargs))
