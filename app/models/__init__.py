# Bedrock
from app.models.embeddings.bedrock_embeddings import BedrockEmbeddings, CustomOllamaEmbeddings
from app.models.inference.bedrock_model import ChatBedrock, CustomOllamaOllama
import os

# OpenAI
# from app.models.embeddings.openai_embeddings import OpenAIEmbeddings
# from app.models.inference.openai_model import ChatOpenAI

ChatModel = ChatBedrock
if os.environ.get('LOCAL_LLM', None):
    ChatModel = CustomOllamaOllama

EmbeddingsModel = BedrockEmbeddings
if os.environ.get('LOCAL_EMBEDDING_MODEL', None):
    EmbeddingsModel = CustomOllamaEmbeddings

# ChatModel = ChatOpenAI
# EmbeddingsModel = OpenAIEmbeddings
