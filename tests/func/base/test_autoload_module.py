import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "autoload"))

from autoload.module_loader import ModuleLoader
from tests.func.base.func_1 import func1
from tests.func.base.func_2 import func2
from tests.func.base.func_3 import func3
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
        module_1 = Module1()
        module_a1 = ModuleA1()
        module_b1 = CustomModuleB1()
        module_c1 = ModuleC1()
        test_cases = (
            ("module_1", module_1),
            ("/module_1.py", module_1),
            ("./module_1", module_1),
            ("..packageA.module_a1", module_a1),
            ("../packageA/module_a1", module_a1),
            ("..packageA.packageB.module_b1", module_b1),
            ("../packageA/packageB/module_b1", module_b1),
            ("/packageC/module_c1", module_c1),
            ("./packageC/module_c1", module_c1),
            (".packageC.module_c1", module_c1),
        )
        for file_name, expected in test_cases:
            with self.subTest(file_name=file_name):
                self.assertEqual(self.loader.load_function(file_name)(), expected)

    def test_load_functions_exclude(self):
        basepkg_result = {Module3(), Module2(), Module1()}
        test_cases = (
            (".", None, basepkg_result),
            (".", [], basepkg_result),
            (".", ["module_3"], {Module2(), Module1()}),
            (".", ["module_3", "module_2"], {Module1()}),
            (".", ("module_3", "module_2"), {Module1()}),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                classes = self.loader.load_functions(pkg_name, exclude)
                instances = set([clazz() for clazz in classes])
                self.assertSetEqual(instances, expected)

    def test_load_functions_complex_path_load(self):
        pkgB_result = {ModuleB3(), ModuleB2(), CustomModuleB1()}
        test_cases = (
            ("../packageA/packageB", None, pkgB_result),
            ("..packageA.packageB", None, pkgB_result),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                classes = self.loader.load_functions(pkg_name, exclude)
                instances = set([clazz() for clazz in classes])
                self.assertSetEqual(instances, expected)

    def test_load_functions_partial_order(self):
        # Only ModuleA1 has order.
        pkgA_result = (ModuleA2(), ModuleA3(), ModuleA1())
        test_cases = (
            ("../packageA", None, pkgA_result),
            ("../packageA/", None, pkgA_result),
            ("..packageA", None, pkgA_result),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                classes = self.loader.load_functions(pkg_name, exclude)
                instances = [clazz() for clazz in classes]
                if not instances[0] == expected[0]:
                    self.fail()
                self.assertSetEqual(set(instances[1:]), set(expected[1:]))

    def test_load_functions_no_order(self):
        # Module1 has other python package.
        basepkg_result = {Module3(), Module2(), Module1()}
        test_cases = (
            (".", None, basepkg_result),
            ("", None, basepkg_result),
            ("/", None, basepkg_result),
            ("./", None, basepkg_result),
            ("./", ("module_3", "module_2"), {Module1()}),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                classes = self.loader.load_functions(pkg_name, exclude)
                instances = set([clazz() for clazz in classes])
                self.assertSetEqual(instances, expected)

    def test_load_functions_order(self):
        pkgC_result = (ModuleC3(), ModuleC2(), ModuleC1())
        test_cases = (
            ("packageC", None, pkgC_result),
            (".packageC", None, pkgC_result),
            ("/packageC/", None, pkgC_result),
            ("/packageC", None, pkgC_result),
            ("./packageC", None, pkgC_result),
            ("packageC", [], pkgC_result),
            ("packageC", ["module_c2"], (ModuleC3(), ModuleC1())),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                classes = self.loader.load_functions(pkg_name, exclude)
                instances = tuple([clazz() for clazz in classes])
                self.assertTupleEqual(instances, expected)

    def test_load_functions_raise_error(self):
        test_cases = (
            ("./nonepackage", None),
            (".", 123),
            (".", [1, 2, 3]),
        )
        for pkg_name, exclude in test_cases:
            with self.assertRaises(Exception):
                self.loader.load_functions(pkg_name, exclude)

if __name__ == '__main__':
    unittest.main()