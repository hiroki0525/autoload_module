from autoload import loadable
from tests.utils import TestClass, test_function


@loadable
class SubLoadClass(TestClass):
    pass


class SubNotLoadClass(TestClass):
    pass


@loadable
@test_function
def sub_load_function():
    pass


def sub_not_load_function():
    pass
