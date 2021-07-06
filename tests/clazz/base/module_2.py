from autoload import load_config

from tests.clazz.testmodule import TestModule


@load_config(load=False)
class Module2(TestModule):
    pass
