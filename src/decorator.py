def load_config(order=None, load=False):
    def decorator(cls):
        if order:
            cls.load_order = order
        cls.load_flg = load
        return cls
    return decorator