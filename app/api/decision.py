from fastapi import APIRouter, Depends

from app.core.security import verify_internal_token
from app.models.schemas import DecisionRequest, DecisionResponse
from app.services.decision_service import decide

router = APIRouter(prefix="/decision", dependencies=[Depends(verify_internal_token)])


@router.post("", response_model=DecisionResponse)
def decide_endpoint(body: DecisionRequest) -> DecisionResponse:
    return decide(body)