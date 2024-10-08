from datetime import datetime
from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.databases.milvus import Milvus


embeddings_router = APIRouter()


class StoreTextRequest(BaseModel):
    """The request to store the embeddings for the given text in the Milvus database."""

    text: str
    source_name: str
    source_id: str
    modified_at: datetime


class DeleteTextRequest(BaseModel):
    """The request to delete the embeddings for the given text from the Milvus database."""
    source_id: str


@embeddings_router.delete('/text/delete')
async def delete_text(
    request: Request,
    delete_text_request: DeleteTextRequest,
) -> dict:
    """Delete the embeddings for the given text from the Milvus database."""
    
    res = await Milvus().delete_embeddings(delete_text_request.source_id)
    return {
        'status': 'success',
        'details': res,
    }


@embeddings_router.post('/text/store')
async def store_text(
    request: Request,
    store_text_request: StoreTextRequest,
) -> dict:
    """Store the embeddings for the given text in the Milvus database."""
    
    ids = await Milvus().split_and_store_text(
        store_text_request.text,
        metadata={
            'source_name': store_text_request.source_name,
            'source_id': store_text_request.source_id,
            'modified_at': store_text_request.modified_at.isoformat(),
        }
    )
    return {'ids': ids}
