from autoload import load_config
from tests.func.testfunction import test_function


@load_config(load=True)
@test_function
def package_b_func1():
    pass
