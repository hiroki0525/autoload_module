"""
This is test file.
You should run this in Docker container.
"""

from autoload.module_loader import ModuleLoader

def main():
    print("start test")
    loader = ModuleLoader()
    print(loader.load_class(".clazz.base.module_1"))
    print(loader.load_classes("clazz.packageA"))
    print(loader.load_function("./func/base/func1.py"))
    print(loader.load_function("/func/packageA"))
    print("end test")

if __name__ == "__main__":
    main()