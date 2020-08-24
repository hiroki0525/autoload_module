def load_config(order=None, module_name=None):
    def decorator(cls):
        if order:
            cls.load_order = order
        if module_name:
            cls.load_module_name = module_name
        return cls
    return decorator