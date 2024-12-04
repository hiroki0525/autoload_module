from __future__ import annotations

from typing import Callable, Literal, Type, overload

from autoload._metadata import get_metadata

from ._imports import (
    import_resources,
)

__all__ = "autoload"


@overload
def autoload(
    name: str,
    type: Literal["class"],
    *,
    base: str | None = None,
    recursive: bool = False,
) -> list[Type]: ...


@overload
def autoload(
    name: str,
    type: Literal["function"],
    *,
    base: str | None = None,
    recursive: bool = False,
) -> list[Callable]: ...


def autoload(
    name: str,
    type: Literal["class", "function"],
    *,
    base: str | None = None,
    recursive: bool = False,
) -> list[Type] | list[Callable]:
    """Import Python package or module and return classes or functions.

    :param name: Package or module name like 'package.module'.
    :param type: Type of the object to import.
    :param base: Base package name like 'package.sub_package'.
        It is necessary to specify this if you set the `name` as a relative path.
    :param recursive: If True, import package recursively.
    :return: Class or function objects.
    """
    objs = import_resources(name, type, base=base, recursive=recursive)
    order_objs: list[tuple[int, Type] | tuple[int, Callable]] = []
    no_order_objs = []
    for obj in objs:
        metadata = get_metadata(obj)
        if not metadata:
            continue
        order = metadata["order"]
        if order is None:
            no_order_objs.append(obj)
            continue
        order_objs.append((order, obj))
    if not order_objs:
        return objs
    sorted_objs = [objs[1] for objs in sorted(order_objs, key=lambda m: m[0])]
    if no_order_objs:
        return sorted_objs + no_order_objs
    return sorted_objs
