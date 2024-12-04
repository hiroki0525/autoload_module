from autoload import loadable
from tests.utils import test_function


@loadable(order=2)
@test_function
def order_2_function():
    pass
