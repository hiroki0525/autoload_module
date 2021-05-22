from autoload import load_config


@load_config(order=1)
def packageC_func3():
    return 'packageC_func3'