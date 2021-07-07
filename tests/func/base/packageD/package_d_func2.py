from autoload import load_config
from tests.func.testfunction import test_function


@test_function
def not_load():
    pass


@load_config(order=4)
@test_function
def multiple4():
    pass


@load_config(order=5)
@test_function
def multiple5():
    pass
