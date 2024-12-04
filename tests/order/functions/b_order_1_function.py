from autoload import loadable
from tests.utils import test_function


@loadable(order=1)
@test_function
def order_1_function():
    pass
