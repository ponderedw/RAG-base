import os
model_type, model_id = os.environ['LLM_MODEL_ID'].split(':', 1)
model_type_embedding, model_id_embedding = \
    os.environ.get('EMBEDDING_MODEL', 'bedrock:').split(':', 1)

if model_type == 'bedrock':
    from app.models.inference.bedrock_model import ChatBedrock
    ChatModel = ChatBedrock
elif model_type == 'ollama':
    from app.models.inference.ollama_model import CustomChatOllama
    ChatModel = CustomChatOllama
elif model_type == 'openai':
    from app.models.inference.openai_model import ChatOpenAI
    ChatModel = ChatOpenAI


if model_type_embedding == 'bedrock':
    from app.models.embeddings.bedrock_embeddings import BedrockEmbeddings
    EmbeddingsModel = BedrockEmbeddings
elif model_type_embedding == 'ollama':
    from app.models.embeddings.ollama_embeddings import CustomOllamaEmbeddings
    EmbeddingsModel = CustomOllamaEmbeddings
elif model_type_embedding == 'openai':
    from app.models.embeddings.openai_embeddings import OpenAIEmbeddings
    EmbeddingsModel = OpenAIEmbeddings
