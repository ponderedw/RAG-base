import json
import uuid


from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, BaseMessage, SystemMessage, ToolMessage, AIMessage, AIMessageChunk

from app.server.llm import get_llm_agent
from app.utils.config import Config


chat_router = APIRouter()


class ChatRequest(BaseModel):
    message: str


class StreamMessage:
    """A fake message that resembles the message structure of LangChain.
    
    Used to provide the process task with a unified structure when handling agent events and state.
    """
    def __init__(self, msg_type: str, content: str = '', tool_calls: list[dict] = None):
        self.msg_type = msg_type
        self.content = content
        self.tool_calls = tool_calls


def get_user_chat_config(session_id: str) -> dict:
    """Get the user chat configuration in a format that's compatible with our chat agent."""
    return {"configurable": {"thread_id": session_id}}


def process_message(message: BaseMessage | StreamMessage) -> dict:
    """Convert a message to a format that can be sent to the client."""
    
    # Mapping of message types to the types used in the client.
    message_type_lookup = {
        HumanMessage: 'human',
        SystemMessage: 'system',
        ToolMessage: 'tool',
        AIMessage: 'ai',
        AIMessageChunk: 'ai',
        StreamMessage: 'system',
    }

    # Default values for message attributes.
    message_type = getattr(message, 'msg_type', message_type_lookup[type(message)])
    content = message.content
    payload = {}

    # Special handling for tool related messages.
    if getattr(message, 'tool_calls', None):
        content = 'Searching Vector DB'
        payload = {'search_query': message.tool_calls[0]['args'].get('query')}
        message_type = 'system'
    elif message_type == 'tool':
        content = 'Analyzing retrieved data for answers'
        payload = {'retrieved_data': message.content}
        message_type = 'system'
    elif message_type == 'ai':
        content = message.content[0]['text']

    return {
        'type': message_type,
        'content': content,
    } | ({'payload': payload} if payload else {})


@chat_router.post("/new")
async def new_chat(request: Request):
    """Create a new chat session."""
    request.session['chat_session_id'] = f'user_{uuid.uuid4()}'
    return {'results': 'ok'}


@chat_router.get("/history")
async def chat_history(request: Request):
    """Get the chat history for the current session.
    
    Note that if there is no chat session, this will return an empty list.
    """

    try:
        # Get the user chat configuration.
        user_config = get_user_chat_config(request.session['chat_session_id'])
    except KeyError:
        # If there is no chat session, return an empty list.
        chat_history = []
    else:
        # Get the chat history from the agent and convert it to a format that can be sent to the client.
        async with get_llm_agent() as llm_agent:
            state = await llm_agent.aget_state(user_config)
        chat_history = [process_message(message) for message in state.values['messages']]

    return {'messages': chat_history}


@chat_router.post("/ask")
async def chat(
    request: Request,
    chat_request: ChatRequest,
):
    """Chat with the LLM agent.
    
    This endpoint will send the user's message to the LLM agent and return the agent's response.

    The response will be a stream of JSON objects, each representing the current state in the processing
    of the user's message.
    """

    # Get or create a chat session ID.
    if 'chat_session_id' not in request.session:
        await new_chat(request)
    session_id = request.session['chat_session_id']

    # Get the user chat configuration and the LLM agent.
    user_config = get_user_chat_config(session_id)

    async def stream_agent_response():
        """Stream the agent's response to the client."""

        async with get_llm_agent() as llm_agent:

            # Send the user's message to the agent and yield the agent's response.
            async for event in llm_agent.astream_events(
                {"messages": [HumanMessage(content=chat_request.message)]},
                config=user_config,
                version='v2',
            ):
                match event['event']:
                    case 'on_retriever_start':
                        # Sending a request to the retriever tool. Let the client know the search terms and the status.
                        yield json.dumps(process_message(StreamMessage(msg_type='ai', tool_calls=[{'args': {'query': event['data']['input']['query']}}]))) + '\n'
                    case 'on_retriever_end':
                        # Retrieval is done. Let the client know the results.
                        print(event['data']['output'], flush=True)
                        yield json.dumps(process_message(StreamMessage(msg_type='tool', content=json.dumps([{
                            'source_name': document.metadata['source_name'],
                            'source_id': document.metadata['source_id'],
                            'modified': document.metadata['modified_at'],
                            'content': document.page_content,
                        } for document in event['data']['output']])))) + '\n'
                    case 'on_chat_model_stream' if event['data']['chunk'].content:

                        # If the message is a tool call, just print a debug message.
                        if event['data']['chunk'].content[0]['type'] in ('tool_use', 'tool_call'):
                            print('Stream.tool_calls:', event['data']['chunk'].tool_calls, flush=True)
                        elif Config.get_deploy_env() != 'LOCAL':
                            # The agent's response. A few tokens at a time.
                            yield json.dumps(process_message(event['data']['chunk'])) + '\n'
                        else:
                            # When working locally, especially with `curl` it's easier to see the output in this more readable format.
                            yield process_message(event['data']['chunk'])['content'] + ' | '
                    case \
                        'on_chat_model_start' | 'on_chain_start' | 'on_chain_end' | 'on_chat_model_stream' \
                        | 'on_chat_model_end' | 'on_chain_stream' | 'on_tool_start' | 'on_tool_end':
                        
                        # Mainly for debug purposes.
                        print('Ignoring message', event['event'])
                    case _:
                        print('Unknown event', event)

            # Let the client know that the conversation is done.
            yield json.dumps(process_message(SystemMessage(content='Done'))) + '\n'

    # Return the agent's response as a stream of JSON objects.
    return StreamingResponse(stream_agent_response(), media_type='application/json')
