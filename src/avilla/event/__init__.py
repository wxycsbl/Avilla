from contextvars import Token
from typing import Dict, Generic, Union
import typing
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface

from avilla.entity import Entity
from avilla.group import Group, T_GroupProfile
from avilla.message.chain import MessageChain
from avilla.relationship import Relationship, T_Profile
from ..context import ctx_relationship, ctx_protocol
from datetime import datetime

class AvillaEvent(Dispatchable, Generic[T_Profile, T_GroupProfile]):
    entity_or_group: Union[Entity[T_Profile], Group[T_Profile, T_GroupProfile]]

    current_id: str  # = Field(default_factory=lambda: ctx_relationship.get().current.id)
    time: datetime  # = Field(default_factory=datetime.now)


_Dispatcher_Tokens: Dict[int, Token[Relationship]] = {}


class RelationshipDispatcher(BaseDispatcher):  # Avilla 将自动注入...哦, 看起来没这个必要.
    @staticmethod
    async def beforeExecution(interface: "DispatcherInterface"):
        rs = ctx_protocol.get().getRelationship(interface.event.entiry_or_group)
        token = ctx_relationship.set(rs)
        _Dispatcher_Tokens[id(interface.event)] = token

    @staticmethod
    async def afterExecution(interface: "DispatcherInterface"):
        del _Dispatcher_Tokens[id(interface.event)]

    @staticmethod
    async def catch(interface: "DispatcherInterface"):
        if typing.get_origin(interface.annotation) is Relationship or interface.annotation is Relationship:
            return ctx_relationship.get()


class MessageChainDispatcher(BaseDispatcher):
    @staticmethod
    async def catch(interface: "DispatcherInterface"):
        if interface.annotation is MessageChain:
            return interface.event.message
