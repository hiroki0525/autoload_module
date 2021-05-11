from autoload.decorator import load_config
from tests.clazz.test_module import TestModule


@load_config(load=True, order=6)
class ModuleD6(TestModule):
    pass
