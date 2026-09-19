import logging
import time

from app.models.schemas import DecisionRequest, DecisionResponse
from app.policy.infer import infer

logger = logging.getLogger(__name__)


def decide(request: DecisionRequest) -> DecisionResponse:
    start = time.perf_counter()
    try:
        return DecisionResponse(vehicleId=infer(request.queue, request.occupant))
    finally:
        ms = (time.perf_counter() - start) * 1000.0
        logger.debug("decision latency_ms=%.3f", ms)
