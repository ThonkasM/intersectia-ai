from pydantic import BaseModel, ConfigDict, Field


class QueuedVehicle(BaseModel):
    id: str
    from_: str = Field(alias="from")  # N, S, E, W
    waitedSeconds: float
    model_config = ConfigDict(populate_by_name=True)


class DecisionRequest(BaseModel):
    queue: list[QueuedVehicle]
    occupant: QueuedVehicle | None = None


class DecisionResponse(BaseModel):
    vehicleId: str | None = None


class ChatRequest(BaseModel):
    message: str
    sessionId: str | None = None


class ChatResponse(BaseModel):
    answer: str


class ChatTopicInfo(BaseModel):
    slug: str
    titulo: str
    categoria: str


class TopicsResponse(BaseModel):
    topics: list[ChatTopicInfo]