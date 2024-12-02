from __future__ import annotations

import inspect
from typing import Any, Callable, ClassVar, cast

from typing_extensions import override

from ._globals import LoadType


class Context:
    __class_context: ClassVar[_ClassContext | None] = None
    __function_context: ClassVar[_FunctionContext | None] = None

    def __new__(cls, *args: Any, **kargs: Any) -> Context:  # noqa: ANN401, PYI034
        load_type = cast(LoadType, args[0] or kargs.get("load_type"))
        if load_type == LoadType.clazz:
            if cls.__class_context is None:
                cls.__class_context = _ClassContext(load_type)
            return cls.__class_context
        if cls.__function_context is None:
            cls.__function_context = _FunctionContext(load_type)
        return cls.__function_context

    def __init__(self, load_type: LoadType) -> None:
        self.__load_type = load_type

    @property
    def load_type(self) -> LoadType:
        return self.__load_type

    def predicate(self) -> Callable[[object], bool]:
        raise NotImplementedError


    def draw_comparison(self, file: str) -> str:
        raise NotImplementedError


class _ClassContext(Context):
    @override
    def predicate(self) -> Callable[[object], bool]:
        return inspect.isclass

    @override
    def draw_comparison(self, file: str) -> str:
        return "".join([s.capitalize() for s in file.split("_")])


class _FunctionContext(Context):
    @override
    def predicate(self) -> Callable[[object], bool]:
        return inspect.isfunction

    @override
    def draw_comparison(self, file: str) -> str:
        return file.lower()
