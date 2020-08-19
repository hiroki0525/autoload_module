from tests.test_module import TestModule


class ModuleB2(TestModule):
    def __init__(self):
        print(f'{self.__class__.__name__} init!')

    def print(self):
        print(f'{self.__class__.__name__} method!')