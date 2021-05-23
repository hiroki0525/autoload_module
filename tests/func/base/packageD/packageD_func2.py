from autoload import load_config


def not_load():
    return 'not_load'


@load_config(load=True, order=4)
def multiple4():
    return 'multiple4'


@load_config(load=True, order=5)
def multiple5():
    return 'multiple5'