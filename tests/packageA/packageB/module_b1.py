from autoload.decorator import load_config
from tests.test_module import TestModule

@load_config(load=True)
class CustomModuleB1(TestModule):
    pass