from autoload.decorator import load_config
from tests.clazz.test_module import TestModule


class NotLoad(TestModule):
    pass


@load_config(order=4)
class ModuleD4(TestModule):
    pass


@load_config(order=5)
class ModuleD5(TestModule):
    pass
