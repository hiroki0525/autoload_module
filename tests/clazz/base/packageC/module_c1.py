from autoload import load_config
from tests.clazz.testmodule import TestModule


@load_config(order=3)
class ModuleC1(TestModule):
    pass