from autoload.decorator import load_config
from tests.test_module import TestModule


@load_config(order=1)
class ModuleC3(TestModule):
    pass