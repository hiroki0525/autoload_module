from autoload import load_config
from tests.func.testfunction import test_function


@load_config(order=2)
@test_function
def package_c_func2():
    pass
