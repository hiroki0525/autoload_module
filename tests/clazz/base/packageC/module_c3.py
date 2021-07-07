from autoload import load_config
from tests.clazz.testmodule import TestModule


@load_config(order=1)
class ModuleC3(TestModule):
    pass