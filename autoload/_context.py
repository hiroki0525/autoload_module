import inspect
from abc import ABC, abstractmethod
from typing import Optional

from ._globals import LoadType


class Context(ABC):
    def __init__(self, load_type: LoadType):
        self.__load_type = load_type

    @property
    def load_type(self):
        return self.__load_type

    @abstractmethod
    def predicate(self):
        raise Exception("'predicate' method is not defined.")

    @abstractmethod
    def draw_comparison(self, file: str):
        raise Exception("'draw_comparison' method is not defined.")


class _ClassContext(Context):
    def predicate(self):
        return inspect.isclass

    def draw_comparison(self, file: str):
        return "".join([s.capitalize() for s in file.split("_")])


class _FunctionContext(Context):
    def predicate(self):
        return inspect.isfunction

    def draw_comparison(self, file: str):
        return file.lower()


class ContextFactory:
    __class_context: Optional[_ClassContext] = None
    __function_context: Optional[_FunctionContext] = None

    @classmethod
    def get(cls, load_type: LoadType) -> Context:
        if load_type == LoadType.clazz:
            if cls.__class_context is None:
                cls.__class_context = _ClassContext(load_type)
            return cls.__class_context
        if cls.__function_context is None:
            cls.__function_context = _FunctionContext(load_type)
        return cls.__function_context
