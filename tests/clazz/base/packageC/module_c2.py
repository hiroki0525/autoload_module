from autoload import load_config
from tests.clazz.test_module import TestModule


@load_config(order=2)
class ModuleC2(TestModule):
    pass