from autoload import load_config
from tests.func.test_function import test_function


@load_config(order=1)
@test_function
def package_d_func1():
    pass


@load_config(order=3)
@test_function
def multiple3():
    pass


@load_config(order=2)
@test_function
def multiple2():
    pass
