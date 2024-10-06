import contextlib
import os

from functools import lru_cache

from fastapi import Depends
from typing_extensions import Annotated

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.prebuilt import create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_aws import ChatBedrock
from langchain_core.messages import SystemMessage
from langchain_core.prompts.prompt import PromptTemplate

from app.databases.milvus import Milvus
from app.databases.postgres import Database


PROMPT_MESSAGE = """When answering the user question using data from the tools, be sure to:
1. First list the sources you are going to use in your answer. The list of sources should be of the form:
[1] - url | filename | modified_at | (index of document in the retriever's answer (e.g. 0, 4): <The quote that being used>
[2] - ...
2. Add a separator '\n\n+++++++++++++\n\n'
3. Write a concise answer based only on the sources and quotes you listed above.

If you don't know the answer, answer that you don't know based on the information you have.
If you're not sure, state that you're not sure."""


# TODO: Think about how to cache this function. Maybe use a pool of agents?
# @lru_cache
@contextlib.asynccontextmanager
async def get_llm_agent():
    
    # The Retriever in the RAG model.
    retriever = Milvus().as_retriever(search_kwargs={'k': 8})

    # The ChatBot LLM
    llm = ChatBedrock(
        model_id=os.environ['AWS_LLM_MODEL_ID'],
        # region_name=os.environ['AWS_DEFAULT_REGION'],
        model_kwargs=dict(temperature=0),
    )

    # Retriever tool, for the R in RAG.
    tool = create_retriever_tool(
        retriever,
        'Internal_Company_Info_Retriever',
        'Searches and retrieves data from the corpus of documents that the company has',

        # Controls how the returned results will look when passed to the LLM.
        # To see available `variables`, check the `retriever.invoke('some query')[0].metadata.keys()`
        document_prompt=PromptTemplate(
            template_format='jinja2',
            input_variables=['url', 'filename', 'modified_at', 'page_content'],
            # template='Source:\n{source}\nContent:\n{page_content}',
            template='{'
                '"filename": "{{filename}}", '
                '"url": "{{url}}", '
                '"modified": "{{modified_at}}", '
                '"content": "{{page_content|replace(\'"\', \'""\')}}"'
            '}',
        ),
        document_separator='\n',
    )
    tools = [tool]

    async with AsyncPostgresSaver.from_conn_string(Database().get_connection_string()) as checkpointer:
            
        # Create the agent itself.
        yield create_react_agent(
            llm,
            tools,
            checkpointer=checkpointer,
            state_modifier=SystemMessage(PROMPT_MESSAGE),
        )
