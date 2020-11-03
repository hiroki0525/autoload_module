from autoload.decorator import load_config


@load_config(order=3)
def packageC_func1():
    return 'packageC_func1'