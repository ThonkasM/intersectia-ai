from fastapi import APIRouter, Depends

from app.core.security import verify_internal_token
from app.models.schemas import ChatRequest, ChatResponse, ChatTopicInfo, TopicsResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", dependencies=[Depends(verify_internal_token)])

chat_service = ChatService()


@router.post("", response_model=ChatResponse)
def chat(body: ChatRequest) -> ChatResponse:
    answer = chat_service.ask(body.message, body.sessionId or "anon")
    return ChatResponse(answer=answer)


@router.get("/topics", response_model=TopicsResponse)
def topics() -> TopicsResponse:
    return TopicsResponse(
        topics=[ChatTopicInfo(**topic) for topic in chat_service.get_available_topics()]
    )