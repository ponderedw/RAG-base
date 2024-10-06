from fastapi import APIRouter, Request


general_router = APIRouter()


@general_router.get("/hello-world")
async def hello_world(request: Request):
    """Return a simple hello world message."""
    return {'message': 'Hello, world!'}
