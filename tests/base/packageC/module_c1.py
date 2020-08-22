from src.decorator import load_config
from tests.test_module import TestModule


@load_config(order=3)
class ModuleC1(TestModule):
    pass