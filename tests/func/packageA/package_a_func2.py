from autoload import load_config
from tests.func.test_function import test_function


@load_config(order=1)
@test_function
def package_a_func2():
    pass
