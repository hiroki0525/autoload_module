from __future__ import annotations

from typing import Callable, TypeVar, overload

from typing_extensions import ParamSpec

from autoload._metadata import set_metadata

P = ParamSpec("P")
R = TypeVar("R")
F = Callable[P, R]
C = TypeVar("C", bound=type)


@overload
def loadable(obj: C, *, order: int | None = None) -> C: ...


@overload
def loadable(obj: F, *, order: int | None = None) -> F: ...


@overload
def loadable(obj: None = None, *, order: int | None = None) -> Callable[[F], F]: ...


def loadable(
    obj: F | C | None = None, *, order: int | None = None
) -> Callable[[F], F] | F | Callable[[C], C]:
    """Load decorator.

    Args:
        order (int | None): The order in which to load the configuration.

    Returns:
        The decorated class or function.
    """

    def decorator(inner_obj: F | C) -> F | C:
        set_metadata(inner_obj, {"order": order})
        return inner_obj

    return decorator(obj) if obj is not None else decorator
