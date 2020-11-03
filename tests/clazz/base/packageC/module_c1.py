from autoload.decorator import load_config
from tests.clazz.test_module import TestModule


@load_config(order=3)
class ModuleC1(TestModule):
    pass