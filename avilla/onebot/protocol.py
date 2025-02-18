import json
from typing import Any, Final, Optional, cast

from graia.broadcast import Dispatchable

from avilla.core.execution import Execution
from avilla.core.message import MessageChain
from avilla.core.operator import Operator
from avilla.core.platform import Adapter, Base, Medium, Platform
from avilla.core.protocol import BaseProtocol
from avilla.core.relationship import Relationship
from avilla.core.selectors import entity as entity_selector
from avilla.core.selectors import mainline as mainline_selector
from avilla.core.selectors import resource as resource_selector
from avilla.core.stream import Stream
from avilla.core.utilles.selector import Selector
from avilla.onebot.event_parse import OnebotEventParser
from avilla.onebot.execution_ensure import OnebotExecutionHandler
from avilla.onebot.message_parse import OnebotMessageParser
from avilla.onebot.message_serialize import OnebotMessageSerializer
from avilla.onebot.operator import OnebotOperator
from avilla.onebot.service import OnebotService


class OnebotProtocol(BaseProtocol):
    platform: Final[Platform] = Platform(
        Base(supplier="Tencent", name="qq", humanized_name="QQ"),
        Medium(
            supplier="howmanybots@github",
            name="onebot",
            humanized_name="OneBot",
            generation="v11",
            version="11",
        ),
        Adapter(
            supplier="GraiaProject@github",
            name="onebot-protocol",
            humanized_name="OneBot for Avilla",
            version="unknown",
        ),
    )

    required_components = {"http.universal_client"}

    execution_handler: Final[OnebotExecutionHandler] = OnebotExecutionHandler()
    message_parser: Final[OnebotMessageParser] = OnebotMessageParser()
    message_serializer: Final[OnebotMessageSerializer] = OnebotMessageSerializer()
    event_parser: Final[OnebotEventParser] = OnebotEventParser()
    service: OnebotService

    def __post_init__(self) -> None:
        if self.avilla.has_service(OnebotService):
            self.service = self.avilla.get_service(OnebotService)  # type: ignore
        else:
            self.service = OnebotService(self)
            self.avilla.add_service(self.service)

    async def ensure_execution(self, execution: Execution):
        return await self.execution_handler.trig(self, execution)

    async def parse_message(self, data: list) -> MessageChain:
        return await self.message_parser.parse(self, data)

    async def parse_event(self, data: dict) -> Optional[Dispatchable]:
        return await self.event_parser.parse(self, data)

    async def serialize_message(self, message: MessageChain) -> list:
        return await self.message_serializer.serialize(self, message)

    async def get_relationship(self, ctx: Selector, current_self: entity_selector) -> Relationship:
        if isinstance(ctx, entity_selector):
            return Relationship(self, ctx, ctx.path["mainline"], current_self)
        raise ValueError("cannot parse select")

    def get_operator(self, account: entity_selector, target: Selector) -> Operator:
        return OnebotOperator(
            self,
            account,
            target if isinstance(target, entity_selector) else None,
            target if isinstance(target, mainline_selector) else None,
        )

    async def fetch_resource(self, resource: resource_selector) -> Stream[Any]:
        async with self.service.access_resource(resource) as accessor:
            status, stream = await accessor.read()
            stream = cast(Stream[Any], stream)
            if status.available:
                return stream
            else:
                raise ValueError(f"resource cannot fetch: {resource}")
