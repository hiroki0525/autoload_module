def load_config(order=None, filename=None):
    def decorator(cls):
        if order:
            cls.load_order = order
        if filename:
            cls.load_filename = filename
        return cls
    return decorator