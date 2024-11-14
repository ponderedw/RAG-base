import json
import uuid

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.server.llm import LLMAgent, LLMEventType
from app.utils.config import Config


chat_router = APIRouter()


class ChatRequest(BaseModel):
    message: str


def get_user_chat_config(session_id: str) -> dict:
    """Get the user chat configuration in a format that's compatible with our chat agent."""
    return {'configurable': {'thread_id': session_id}}


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
        async with LLMAgent() as llm_agent:
            chat_history = await llm_agent.aget_history(user_config)
            
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

        async with LLMAgent() as llm_agent:

            # Send the user's message to the agent and yield the agent's response.
            async for chat_msg in llm_agent.astream_events(chat_request.message, user_config):
                if chat_msg.type == LLMEventType.CHAT_CHUNK and Config.get_deploy_env() == 'LOCAL':
                    # When working locally, especially with `curl`,
                    # it's easier to see the output in this more readable format.
                    yield chat_msg.content + ' | '
                else:
                    yield json.dumps(chat_msg.to_dict()) + '\n'

    # Return the agent's response as a stream of JSON objects.
    return StreamingResponse(stream_agent_response(), media_type='application/json')
