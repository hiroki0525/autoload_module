from src.decorator import load_config
from tests.test_module import TestModule


@load_config(order=1)
class ModuleA2(TestModule):
    def __init__(self):
        print(f'{self.__class__.__name__} init!')

    def print(self):
        print(f'{self.__class__.__name__} method!')