from autoload import load_config
from tests.clazz.testmodule import TestModule


@load_config(order=1)
class ModuleD1(TestModule):
    pass


@load_config(order=3)
class ModuleD3(TestModule):
    pass


@load_config(order=2)
class ModuleD2(TestModule):
    pass
