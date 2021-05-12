from autoload.decorator import load_config
from tests.clazz.test_module import TestModule


@load_config(load=True, order=2)
class ModuleD2(TestModule):
    pass


@load_config(load=True, order=1)
class ModuleD1(TestModule):
    pass


@load_config(load=True, order=3)
class ModuleD3(TestModule):
    pass