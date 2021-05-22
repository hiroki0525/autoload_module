from autoload import load_config
from tests.clazz.test_module import TestModule


@load_config()
class CustomModuleB1(TestModule):
    pass
