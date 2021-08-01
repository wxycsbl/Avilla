from typing import TYPE_CHECKING, Optional

from pydantic.main import BaseModel


from avilla.entity import Entity

from . import Operation


class RequestHandle(BaseModel, Operation[str]):
    ...


class RequestApprove(RequestHandle):
    def __init__(self, request_id: str) -> None:
        super().__init__(target=request_id)


class RequestDeny(RequestHandle):
    reason: Optional[str] = None
    block: bool = False

    def __init__(self, request_id: str, *, reason: Optional[str] = None, block: bool = False) -> None:
        super().__init__(target=request_id, reason=reason, block=block)


class RequestIgnore(RequestHandle):
    block: bool = False

    def __init__(self, request_id: str, *, block: bool = False) -> None:
        super().__init__(target=request_id, block=block)
