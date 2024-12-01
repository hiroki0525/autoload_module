from __future__ import annotations

import inspect
from abc import ABC, abstractmethod
from typing import Callable

from ._globals import LoadType


class Context(ABC):
    def __init__(self, load_type: LoadType) -> None:
        self.__load_type = load_type

    @property
    def load_type(self) -> LoadType:
        return self.__load_type

    @abstractmethod
    def predicate(self) -> Callable[[object], bool]: ...

    @abstractmethod
    def draw_comparison(self, file: str) -> str: ...


class _ClassContext(Context):
    def predicate(self) -> Callable[[object], bool]:
        return inspect.isclass

    def draw_comparison(self, file: str) -> str:
        return "".join([s.capitalize() for s in file.split("_")])


class _FunctionContext(Context):
    def predicate(self) -> Callable[[object], bool]:
        return inspect.isfunction

    def draw_comparison(self, file: str) -> str:
        return file.lower()


class ContextFactory:
    __class_context: _ClassContext | None = None
    __function_context: _FunctionContext | None = None

    @classmethod
    def get(cls, load_type: LoadType) -> Context:
        if load_type == LoadType.clazz:
            if cls.__class_context is None:
                cls.__class_context = _ClassContext(load_type)
            return cls.__class_context
        if cls.__function_context is None:
            cls.__function_context = _FunctionContext(load_type)
        return cls.__function_context
