"""AI agent chat API router."""

from fastapi import APIRouter

from models.schemas import ChatRequest, ChatResponse
from services.agent import process_message

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """Process a user chat message through the AI agent."""
    history = [{"role": m.role, "content": m.content} for m in request.messages]
    reply, action, filters = await process_message(history)
    return ChatResponse(reply=reply, action=action, filters=filters)
