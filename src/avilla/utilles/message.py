from typing import Any, Awaitable, Callable, Dict, Generic, List, Type, TypeVar

from avilla.message.chain import MessageChain
from avilla.message.element import Element
from avilla.typing import T_Protocol

T = TypeVar("T", bound=Element)


class MessageSerializeBus(Generic[T_Protocol]):
    message_serializers: Dict[Type[Element], Callable[[T_Protocol, Any], Awaitable[Any]]]

    def __init__(self) -> None:
        pass

    def register(self, message_type: Type[T]):
        def wrapper(func: Callable[[T_Protocol, T], Any]):
            self.message_serializers[message_type] = func
            return func

        return wrapper

    async def serialize(self, protocol: T_Protocol, message: MessageChain) -> List[Any]:
        result = []

        for element in message.__root__:
            message_type = element.__class__
            if message_type in self.message_serializers:
                result.append(await self.message_serializers[message_type](protocol, element))
            else:
                raise ValueError(f"[{message_type}] cannot be serialized.")

        return result
