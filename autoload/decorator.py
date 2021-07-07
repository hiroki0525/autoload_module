__all__ = "load_config"

from typing import Callable, Optional

from autoload._globals import Class_Or_Func, DecoratorVal


def load_config(
    order: Optional[int] = None, load: bool = True
) -> Callable[[Class_Or_Func], Class_Or_Func]:
    def decorator(resource: Class_Or_Func):
        if order:
            setattr(resource, DecoratorVal.order.value, order)
        setattr(resource, DecoratorVal.flg.value, load)
        return resource

    return decorator
