from autoload import load_config
from tests.clazz.testmodule import TestModule


@load_config()
class CustomModuleB1(TestModule):
    pass
