__all__ = "load_config"

from typing import Optional


def load_config(order: Optional[int] = None, load: bool = True):
    def decorator(resource):
        if order:
            resource._load_order = order
        resource._load_flg = load
        return resource

    return decorator
