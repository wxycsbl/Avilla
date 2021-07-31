from typing import TYPE_CHECKING, Awaitable, Callable, Coroutine, NoReturn, Optional

from pydantic.main import BaseModel

from pathlib import Path

from avilla.message.element import Element
from avilla.resource import Resource
from avilla.provider import Provider, RawProvider


class PlainText(Element):
    text: str

    def __init__(self, text: str) -> NoReturn:
        """实例化一个 Plain 消息元素, 用于承载消息中的文字.

        Args:
            text (str): 元素所包含的文字
        """
        super().__init__(text=text)

    def asDisplay(self) -> str:
        return self.text


class Notice(Element):
    """该消息元素用于承载消息中用于提醒/呼唤特定用户的部分."""

    target: str

    def __init__(self, target: str, **kwargs) -> None:
        """实例化一个 Notice 消息元素, 用于承载消息中用于提醒/呼唤特定用户的部分.

        Args:
            target (str): 需要提醒/呼唤的特定用户的 ID.
        """
        super().__init__(target=target, **kwargs)

    def asDisplay(self) -> str:
        return f"[$Notice:{self.target}]"


class NoticeAll(Element):
    "该消息元素用于群组中的管理员提醒群组中的所有成员"

    def __init__(_) -> None:
        super().__init__()

    def asDisplay(self) -> str:
        return "[$NoticeAll]"


class Image(BaseModel, Resource[Provider[bytes]]):
    def __init__(self, content: bytes):
        self.provider = RawProvider(content)

    @classmethod
    def fromLocalFile(cls, path: Path):
        data = path.read_bytes()
        return cls(data)

    # py 没有方法重载, 也没有扩展方法, 真是 toy.


class Quote(Element):
    id: str
