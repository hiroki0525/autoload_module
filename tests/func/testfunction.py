def test_function(func):
    def wrapper():
        return func.__name__

    return wrapper
