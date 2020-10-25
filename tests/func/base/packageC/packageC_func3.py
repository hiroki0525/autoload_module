from autoload.decorator import load_config


@load_config(order=1)
def packageC_func3():
    pass