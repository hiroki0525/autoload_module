from autoload import load_config
from tests.clazz.test_module import TestModule


@load_config(order=1)
class ModuleA2(TestModule):
    pass