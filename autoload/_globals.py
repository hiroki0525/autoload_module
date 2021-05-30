from enum import Enum
from typing import Any, Callable, Type, TypeVar


class LoadType(Enum):
    func = "function"
    clazz = "class"


Class_Or_Func = TypeVar("Class_Or_Func", Type[Any], Callable)
