from autoload import load_config

@load_config(load=True)
def packageB_func1():
    return 'packageB_func1'