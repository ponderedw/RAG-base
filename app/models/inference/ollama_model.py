import os

from langchain_ollama import ChatOllama


class CustomChatOllama(ChatOllama):
    """A wrapper for the `langchain_aws.ChatBedrock`."""

    def __init__(self, **kwargs):
        """Initialize the `ChatBedrock` with specific configuration."""
        model_type, model_id = os.environ['LLM_MODEL_ID'].split(':', 1)
        default_kwargs = {
            'model': model_id,
            'base_url': 'http://local_model:11434'
        }

        super().__init__(**(default_kwargs | kwargs))
