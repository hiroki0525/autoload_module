def load_config(order=None):
    def decorator(cls):
        if order:
            cls.load_order = order
        return cls
    return decorator