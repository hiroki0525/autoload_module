import sys
import unittest
from pathlib import Path

from tests.func.base.packageD.package_d_func1 import multiple2, multiple3, package_d_func1
from tests.func.base.packageD.package_d_func2 import multiple4, multiple5
from tests.func.base.packageD.package_d_func3 import package_d_func3

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "autoload"))

from autoload import ModuleLoader
from autoload.exception import LoaderStrictModeError
from tests.func.base.func1 import func1
from tests.func.base.func2 import func2
from tests.func.base.func3 import func3
from tests.func.base.packageC.package_c_func1 import package_c_func1
from tests.func.base.packageC.package_c_func2 import package_c_func2
from tests.func.base.packageC.package_c_func3 import package_c_func3
from tests.func.packageA.package_a_func1 import package_a_func1
from tests.func.packageA.package_a_func3 import package_a_func3
from tests.func.packageA.package_a_func2 import package_a_func2
from tests.func.packageA.packageB.package_b_func1 import package_b_func1
from tests.func.packageA.packageB.package_b_func2 import package_b_func2
from tests.func.packageA.packageB.package_b_func3 import package_b_func3


class TestAutoLoadModule(unittest.TestCase):

    def setUp(self):
        print('setup')
        self.loader = ModuleLoader()

    def test_load_function(self):
        result_1 = func1()
        result_A_1 = package_a_func1()
        result_B_1 = package_b_func1()
        result_C_1 = package_c_func1()
        # Importing path test runs on class base test.
        test_cases = (
            ("func1", result_1),
            ("..packageA.package_a_func1", result_A_1),
            ("../packageA/packageB/package_b_func1", result_B_1),
            ("/packageC/package_c_func1", result_C_1),
        )
        for file_name, expected in test_cases:
            with self.subTest(file_name=file_name):
                self.assertEqual(self.loader.load_function(file_name)(), expected)

    def test_load_functions_exclude(self):
        basepkg_result = {func3(), func2(), func1()}
        test_cases = (
            (".", None, basepkg_result),
            (".", [], basepkg_result),
            (".", ["func3"], {func2(), func1()}),
            (".", ["func3", "func2"], {func1()}),
            (".", ("func3", "func2"), {func1()}),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                functions = self.loader.load_functions(pkg_name, exclude)
                results = set([function() for function in functions])
                self.assertSetEqual(results, expected)

    def test_load_functions_complex_path_load(self):
        pkgB_result = {package_b_func3(), package_b_func2(), package_b_func1()}
        test_cases = (
            ("../packageA/packageB", None, pkgB_result),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                functions = self.loader.load_functions(pkg_name, exclude)
                results = set([function() for function in functions])
                self.assertSetEqual(results, expected)

    def test_load_functions_partial_order(self):
        # Only ModuleA1 has order.
        pkgA_result = (package_a_func2(), package_a_func3(), package_a_func1())
        test_cases = (
            ("../packageA/", None, pkgA_result),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                functions = self.loader.load_functions(pkg_name, exclude)
                results = [function() for function in functions]
                if not results[0] == expected[0]:
                    self.fail()
                self.assertSetEqual(set(results[1:]), set(expected[1:]))

    def test_load_functions_no_order(self):
        # Module1 has other python package.
        basepkg_result = {func3(), func2(), func1()}
        test_cases = (
            ("", None, basepkg_result),
            ("./", ("func3", "func2"), {func1()}),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                functions = self.loader.load_functions(pkg_name, exclude)
                results = set([function() for function in functions])
                self.assertSetEqual(results, expected)

    def test_load_functions_order(self):
        pkgC_result = (package_c_func3(), package_c_func2(), package_c_func1())
        test_cases = (
            ("packageC", [], pkgC_result),
            ("packageC", ["package_c_func2"], (package_c_func3(), package_c_func1())),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                functions = self.loader.load_functions(pkg_name, exclude)
                results = tuple([function() for function in functions])
                self.assertTupleEqual(results, expected)

    def test_load_functions_raise_error(self):
        test_cases = (
            ("./nonepackage", None),
            (".", 123),
            (".", [1, 2, 3]),
        )
        for pkg_name, exclude in test_cases:
            with self.assertRaises(Exception):
                self.loader.load_functions(pkg_name, exclude)

    def test_load_functions_recursive(self):
        pkgA_result = {package_a_func2(), package_a_func3(), package_a_func1()}
        pkgB_result = {package_b_func3(), package_b_func2(), package_b_func1()}
        test_cases = (
            ("../packageA", False, pkgA_result),
            # expected packageA is ordered, B is random.
            ("../packageA", True, pkgA_result | pkgB_result),
        )
        for pkg_name, recursive, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, recursive=recursive):
                functions = self.loader.load_functions(pkg_name, recursive=recursive)
                instances = set([function() for function in functions])
                self.assertSetEqual(instances, expected)

    def test_load_multiple_functions(self):
        basepkg_result = {package_d_func1(), multiple2(), multiple3(), multiple4(), multiple5(), package_d_func3()}
        test_cases = (
            ("packageD", None, basepkg_result),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                functions = self.loader.load_functions(pkg_name, exclude)
                results = set([function() for function in functions])
                self.assertSetEqual(results, expected)

    def test_strict_mode(self):
        self.loader = ModuleLoader(strict=True)
        self.test_load_functions_exclude()
        self.test_load_functions_partial_order()
        self.test_load_functions_no_order()
        self.test_load_functions_order()

    def test_strict_mode_raise_error(self):
        self.loader = ModuleLoader(strict=True)
        test_cases = (
            "packageD",
            # 'load_classes' will be able to load not only package but also module.
            # "packageD.module_d1"
        )
        for pkg_name in test_cases:
            with self.assertRaises(LoaderStrictModeError):
                try:
                    self.loader.load_functions(pkg_name)
                except LoaderStrictModeError as e:
                    # check message
                    print(e)
                    raise e


if __name__ == '__main__':
    unittest.main()
