from autoload.decorator import load_config
from tests.func.test_module import TestModule


@load_config(order=2)
class ModuleC2(TestModule):
    pass