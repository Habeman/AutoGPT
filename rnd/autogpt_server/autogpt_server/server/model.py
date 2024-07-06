import enum
import typing

import pydantic

class Methods(enum.Enum):
    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    UPDATE = "update"
    ERROR = "error"


class WsMessage(pydantic.BaseModel):
    method: Methods
    data: typing.Dict[str, typing.Any] | None = None
    success: bool | None = None
    channel: str | None = None
    error: str | None = None


class ExecutionSubscription(pydantic.BaseModel):
    graph_id: str


class SubscriptionDetails(pydantic.BaseModel):
    event_type: str
    channel: str
    graph_id: str
