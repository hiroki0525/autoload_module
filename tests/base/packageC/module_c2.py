from src.decorator import load_config


@load_config(order=2)
class ModuleC2:
    pass