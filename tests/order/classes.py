from autoload import loadable
from tests.utils import TestClass


@loadable(order=3)
class Order3Class(TestClass):
    pass


@loadable(order=1)
class Order1Class(TestClass):
    pass


@loadable
class Order4Class(TestClass):
    pass


@loadable(order=2)
class Order2Class(TestClass):
    pass
