from autoload import loadable
from tests.utils import TestClass, test_function


@loadable
class MainLoadClass(TestClass):
    pass


class MainNotLoadClass(TestClass):
    pass


@loadable
@test_function
def main_load_function():
    pass


def main_not_load_function():
    pass
