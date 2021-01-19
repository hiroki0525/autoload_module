import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "autoload"))

from autoload.module_loader import ModuleLoader
from tests.func.base.func1 import func1
from tests.func.base.func2 import func2
from tests.func.base.func3 import func3
from tests.func.base.packageC.packageC_func1 import packageC_func1
from tests.func.base.packageC.packageC_func2 import packageC_func2
from tests.func.base.packageC.packageC_func3 import packageC_func3
from tests.func.packageA.packageA_func1 import packageA_func1
from tests.func.packageA.packageA_func3 import packageA_func3
from tests.func.packageA.packageA_func2 import packageA_func2
from tests.func.packageA.packageB.packageB_func1 import packageB_func1
from tests.func.packageA.packageB.packageB_func2 import packageB_func2
from tests.func.packageA.packageB.packageB_func3 import packageB_func3


class TestAutoLoadModule(unittest.TestCase):

    def setUp(self):
        print('setup')
        self.loader = ModuleLoader()

    def test_load_function(self):
        result_1 = func1()
        result_A_1 = packageA_func1()
        result_B_1 = packageB_func1()
        result_C_1 = packageC_func1()
        # Importing path test runs on class base test.
        test_cases = (
            ("func1", result_1),
            ("..packageA.packageA_func1", result_A_1),
            ("../packageA/packageB/packageB_func1", result_B_1),
            ("/packageC/packageC_func1", result_C_1),
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
        pkgB_result = {packageB_func3(), packageB_func2(), packageB_func1()}
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
        pkgA_result = (packageA_func2(), packageA_func3(), packageA_func1())
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
        pkgC_result = (packageC_func3(), packageC_func2(), packageC_func1())
        test_cases = (
            ("packageC", [], pkgC_result),
            ("packageC", ["packageC_func2"], (packageC_func3(), packageC_func1())),
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
        pkgA_result = {packageA_func2(), packageA_func3(), packageA_func1()}
        pkgB_result = {packageB_func3(), packageB_func2(), packageB_func1()}
        test_cases = (
            ("../packageA", False, pkgA_result),
            # expectd packageA is ordered, B is random.
            ("../packageA", True, pkgA_result | pkgB_result),
        )
        for pkg_name, recursive, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, recursive=recursive):
                functions = self.loader.load_functions(pkg_name, recursive=recursive)
                instances = set([function() for function in functions])
                self.assertSetEqual(instances, expected)

if __name__ == '__main__':
    unittest.main()
