from autoload import load_config
from tests.func.test_function import test_function


@load_config(order=3)
@test_function
def package_c_func1():
    pass
