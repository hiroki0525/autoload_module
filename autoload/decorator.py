__all__ = "load_config"

from typing import Callable, Optional

from autoload._globals import Class_Or_Func


def load_config(
    order: Optional[int] = None, load: bool = True
) -> Callable[[Class_Or_Func], Class_Or_Func]:
    def decorator(resource: Class_Or_Func):
        if order:
            setattr(resource, "_load_order", order)
        setattr(resource, "_load_flg", load)
        return resource

    return decorator
