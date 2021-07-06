from autoload import load_config
from tests.clazz.testmodule import TestModule


@load_config(order=2)
class ModuleC2(TestModule):
    pass