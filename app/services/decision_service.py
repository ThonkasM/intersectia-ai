import logging
import time

from app.models.schemas import DecisionRequest, DecisionResponse
from app.policy.infer import infer

logger = logging.getLogger(__name__)


def decide(request: DecisionRequest) -> DecisionResponse:
    start = time.perf_counter()
    try:
        if request.occupant is not None:
            return DecisionResponse(vehicleId=None)
        if not request.queue:
            return DecisionResponse(vehicleId=None)
        return DecisionResponse(vehicleId=infer(request.queue))
    finally:
        ms = (time.perf_counter() - start) * 1000.0
        logger.info("decision latency_ms=%.3f", ms)