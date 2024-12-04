import functools


class TestClass:
    def __eq__(self, other):
        return self.__class__.__name__ == other


def test_function(func):
    @functools.wraps(func)
    def wrapper():
        return func.__name__

    return wrapper
