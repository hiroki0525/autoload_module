"""Module provides a decorator for loading configuration."""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from autoload._globals import DecoratorVal

__all__ = ["load_config"]

T = TypeVar("T", type[Any], Callable)


def load_config(
    order: int | None = None,
    *,
    load: bool = True,
) -> Callable[[T], T]:
    """Load configuration.

    Args:
        order (int | None): The order in which to load the configuration.
        load (bool): Flag to indicate whether to load the configuration.

    Returns:
        Callable[[Class_Or_Func], Class_Or_Func]: The decorated class or function.

    """

    def decorator(resource: T) -> T:
        if order:
            setattr(resource, DecoratorVal.order.value, order)
        setattr(resource, DecoratorVal.flg.value, load)
        return resource

    return decorator
