from src.decorator import load_config


@load_config(order=3)
class TestC1:
    def __init__(self):
        print(f'{self.__class__.__name__} init!')

    def print(self):
        print(f'{self.__class__.__name__} method!')