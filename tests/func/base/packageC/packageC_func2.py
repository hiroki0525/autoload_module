from autoload.decorator import load_config


@load_config(order=2)
def packageC_func2():
    pass