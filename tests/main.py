"""
This is test file.
You should run this in Docker container.
"""

from autoload.module_loader import ModuleLoader


def main():
    print("--- start test -------------------------")
    loader = ModuleLoader()
    print(f'Base path is {loader.base_path}')
    print(loader.load_class(".tests.clazz.base.module_1"))
    print(loader.load_classes("tests.clazz.packageA"))
    print(loader.load_classes("tests.clazz.packageA", recursive=True))
    print(loader.load_classes("tests.clazz.base.packageD"))
    print(loader.load_function("./tests/func/base/func1.py"))
    print(loader.load_functions("tests/func/packageA"))
    print(loader.load_functions("tests/func/packageA", recursive=True))
    print(loader.load_functions("tests/func/base/packageD"))
    print("--- end test -------------------------")


if __name__ == "__main__":
    main()
