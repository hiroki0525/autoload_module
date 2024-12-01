from enum import Enum
from typing import Callable, Union


class LoadType(Enum):
    func = "function"
    clazz = "class"


class DecoratorVal(Enum):
    flg = "_load_flg"
    order = "_load_order"


Class_Or_Func = Union[type, Callable]
