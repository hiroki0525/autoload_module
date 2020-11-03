from autoload.decorator import load_config


@load_config(load=True, order=2)
def multiple1():
    return 'multiple1'


@load_config(load=True, order=1)
def multiple2():
    return 'multiple2'


@load_config(load=True, order=3)
def multiple3():
    return 'multiple3'