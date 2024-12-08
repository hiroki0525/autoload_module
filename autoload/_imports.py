from __future__ import annotations

import inspect
from importlib import import_module
from importlib.util import find_spec
from pkgutil import iter_modules
from typing import Callable, Literal, overload

from autoload._metadata import has_metadata


@overload
def import_resources_by_module(
    name: str,
    type: Literal["function"],
    *,
    base: str | None = None,
) -> list[Callable]: ...


@overload
def import_resources_by_module(
    name: str,
    type: Literal["class"],
    *,
    base: str | None = None,
) -> list[type]: ...


def import_resources_by_module(
    name: str,
    type: Literal["class", "function"],
    *,
    base: str | None = None,
) -> list[Callable] | list[type]:
    try:
        module = import_module(name, base)
    except Exception:
        return []
    members = inspect.getmembers(
        module, inspect.isclass if type == "class" else inspect.isfunction
    )
    return [obj for _, obj in members if has_metadata(obj)]


@overload
def import_resources(
    name: str,
    type: Literal["function"],
    *,
    base: str | None = None,
    recursive: bool = False,
) -> list[Callable]: ...


@overload
def import_resources(
    name: str,
    type: Literal["class"],
    *,
    base: str | None = None,
    recursive: bool = False,
) -> list[type]: ...


def import_resources(
    name: str,
    type: Literal["class", "function"],
    *,
    base: str | None = None,
    recursive: bool = False,
) -> list[Callable] | list[type]:
    try:
        target_spec = find_spec(name, base)
    except Exception:
        return []
    if target_spec is None:
        return []
    if not target_spec.submodule_search_locations:
        return import_resources_by_module(name, type, base=base)
    package = import_module(name, base)
    results: list = []
    package_name = package.__name__
    for module_info in iter_modules(package.__path__, f"{package_name}."):
        module_info_name = module_info.name
        spec = find_spec(module_info_name)
        if spec is None:
            continue
        if spec.submodule_search_locations and recursive:
            results.extend(
                import_resources(
                    module_info_name,
                    type,
                    base=package_name,
                    recursive=recursive,
                ),
            )
            continue
        results.extend(
            import_resources_by_module(
                module_info_name,
                type,
                base=package_name,
            ),
        )
    return results
