from src.decorator import load_config
from tests.test_module import TestModule


@load_config(order=2)
class ModuleC2(TestModule):
    pass