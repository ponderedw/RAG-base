# Bedrock
from app.models.embeddings.bedrock_embeddings import BedrockEmbeddings
from app.models.inference.bedrock_model import ChatBedrock

# OpenAI
# from app.models.embeddings.openai_embeddings import OpenAIEmbeddings
# from app.models.inference.openai_model import ChatOpenAI


# ChatModel = ChatBedrock
ChatModel = ChatBedrock
EmbeddingsModel = BedrockEmbeddings
