from src.decorator import load_config


@load_config(order=3)
class ModuleC1:
    pass