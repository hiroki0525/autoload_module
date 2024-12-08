from typing import Final

from autoload import autoload

main_package: Final[str] = "main_package"
main_package_name: Final[str] = f"tests.{main_package}"
main_module: Final[str] = "main"
main_module_name: Final[str] = f"{main_package_name}.{main_module}"
sub_package: Final[str] = "sub_package"
sub_package_name: Final[str] = f"{main_package_name}.{sub_package}"

# `name` test


def test_name_existed_module():
    functions = autoload(main_module_name, "function")
    assert len(functions) == 1
    assert functions[0]() == "main_load_function"


def test_name_not_existed_module():
    functions = autoload(f"{main_package}.nothing", "function")
    assert len(functions) == 0


def test_name_existed_package():
    functions = autoload(main_package_name, "function")
    assert len(functions) == 1
    assert functions[0]() == "main_load_function"


def test_name_not_existed_package():
    functions = autoload("tests.nothing", "function")
    assert len(functions) == 0


def test_name_invalid_format():
    functions = autoload(main_module_name.replace(".", "/"), "function")
    assert len(functions) == 0


# `type` test


def test_type_function():
    functions = autoload(main_module_name, "function")
    assert len(functions) == 1
    assert functions[0]() == "main_load_function"


def test_type_class():
    classes = autoload(main_module_name, "class")
    assert len(classes) == 1
    assert classes[0]() == "MainLoadClass"


# `base` test


def test_main_one_relative():
    functions = autoload(f".{main_module}", "function", base=main_package_name)
    assert len(functions) == 1
    assert functions[0]() == "main_load_function"


def test_main_two_relative():
    functions = autoload(f"..{main_module}", "function", base=sub_package_name)
    assert len(functions) == 1
    assert functions[0]() == "main_load_function"


def test_main_complex():
    functions = autoload(
        f"...{main_package}.{main_module}", "function", base=sub_package_name
    )
    assert len(functions) == 1
    assert functions[0]() == "main_load_function"


def test_main_not_existed_package_but_existed_module():
    functions = autoload(
        f"..{main_module}",
        "function",
        base=f"{main_package_name}.nothing",
    )
    assert len(functions) == 1
    assert functions[0]() == "main_load_function"


def test_main_existed_package_but_not_existed_module():
    functions = autoload(
        ".nothing",
        "function",
        base=main_package,
    )
    assert len(functions) == 0


def test_main_invalid_format():
    functions = autoload(
        f".{main_module}", "function", base=main_package_name.replace(".", "/")
    )
    assert len(functions) == 0


# `recursive` test


def test_no_recursive():
    functions = autoload(main_package_name, "function")
    assert len(functions) == 1
    assert functions[0]() == "main_load_function"


def test_recursive_false():
    functions = autoload(main_package_name, "function", recursive=False)
    assert len(functions) == 1
    assert functions[0]() == "main_load_function"


def test_recursive_true():
    functions = autoload(main_package_name, "function", recursive=True)
    assert len(functions) == 2
    assert functions[0]() == "main_load_function"
    assert functions[1]() == "sub_load_function"


# `order` test


def test_order_module():
    classes = autoload("tests.order.classes", "class")
    assert len(classes) == 4
    assert classes[0]() == "Order1Class"
    assert classes[1]() == "Order2Class"
    assert classes[2]() == "Order3Class"
    assert classes[3]() == "Order4Class"


def test_order_package():
    functions = autoload("tests.order.functions", "function")
    assert len(functions) == 4
    assert functions[0]() == "order_1_function"
    assert functions[1]() == "order_2_function"
    assert functions[2]() == "order_3_function"
    assert functions[3]() == "order_4_function"
