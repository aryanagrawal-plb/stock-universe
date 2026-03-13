"""AI agent chat API router."""

from fastapi import APIRouter

from models.schemas import ChatRequest, ChatResponse
from services.agent import process_message

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a user chat message through the AI agent."""
    reply, filters = await process_message(request.message)
    return ChatResponse(reply=reply, filters=filters)
