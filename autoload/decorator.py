__all__ = "load_config"


def load_config(order=None, load=True):
    def decorator(resource):
        if order:
            resource._load_order = order
        resource._load_flg = load
        return resource

    return decorator
