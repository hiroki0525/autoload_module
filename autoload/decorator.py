def load_config(order=None, load=False):
    def decorator(resource):
        if order:
            resource.load_order = order
        resource.load_flg = load
        return resource
    return decorator