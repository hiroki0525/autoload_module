from autoload import loadable
from tests.utils import test_function


@loadable(order=3)
@test_function
def order_3_function():
    pass
