from autoload import load_config
from tests.func.testfunction import test_function


@load_config(order=6)
@test_function
def package_d_func3():
    pass
