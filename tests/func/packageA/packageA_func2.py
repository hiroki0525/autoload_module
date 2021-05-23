from autoload import load_config


@load_config(order=1)
def packageA_func2():
    return 'packageA_func2'