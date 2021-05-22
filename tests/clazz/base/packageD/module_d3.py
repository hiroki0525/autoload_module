from autoload import load_config
from tests.clazz.test_module import TestModule


@load_config(order=6)
class ModuleD6(TestModule):
    pass
