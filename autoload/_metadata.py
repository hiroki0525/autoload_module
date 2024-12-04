from __future__ import annotations

from typing import Callable, TypedDict


class Metadata(TypedDict):
    order: int | None


autoload_metadata: dict[str, Metadata] = {}


def set_metadata(obj: Callable, metadata: Metadata) -> None:
    autoload_metadata[f"{obj.__module__}.{obj.__name__}"] = metadata


def get_metadata(obj: Callable) -> Metadata | None:
    return autoload_metadata.get(f"{obj.__module__}.{obj.__name__}")


def has_metadata(obj: Callable) -> bool:
    return f"{obj.__module__}.{obj.__name__}" in autoload_metadata
