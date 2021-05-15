import sys
import unittest
from pathlib import Path

from tests.clazz.base.packageD.module_d1 import ModuleD1, ModuleD2, ModuleD3
from tests.clazz.base.packageD.module_d2 import ModuleD4, ModuleD5
from tests.clazz.base.packageD.module_d3 import ModuleD6

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "autoload"))

from autoload.module_loader import ModuleLoader
from tests.clazz.base.module_1 import Module1
from tests.clazz.base.module_2 import Module2
from tests.clazz.base.module_3 import Module3
from tests.clazz.base.packageC.module_c1 import ModuleC1
from tests.clazz.base.packageC.module_c2 import ModuleC2
from tests.clazz.base.packageC.module_c3 import ModuleC3
from tests.clazz.packageA.module_a1 import ModuleA1
from tests.clazz.packageA.module_a2 import ModuleA2
from tests.clazz.packageA.module_a3 import ModuleA3
from tests.clazz.packageA.packageB.module_b1 import CustomModuleB1
from tests.clazz.packageA.packageB.module_b2 import ModuleB2
from tests.clazz.packageA.packageB.module_b3 import ModuleB3


class TestAutoLoadModule(unittest.TestCase):

    def setUp(self):
        print('setup')
        self.loader = ModuleLoader()

    def test_initialize(self):
        test_cases = (
            (ModuleLoader('').base_path, '/'),
            (ModuleLoader('/').base_path, '/'),
            (ModuleLoader('/test').base_path, '/test'),
            (ModuleLoader('/test/').base_path, '/test'),
        )
        for path_name, expected in test_cases:
            with self.subTest(path_name=path_name):
                self.assertEqual(path_name, expected)

    def test_load_class(self):
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
                self.assertEqual(self.loader.load_class(file_name)(), expected)

    def test_load_classes_exclude(self):
        # Module2 tagged 'load = False'
        basepkg_result = {Module3(), Module1()}
        test_cases = (
            (".", None, basepkg_result),
            (".", [], basepkg_result),
            (".", ["module_3"], {Module1()}),
            (".", ["module_3", "module_2"], {Module1()}),
            (".", ("module_3", "module_2"), {Module1()}),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                classes = self.loader.load_classes(pkg_name, exclude)
                instances = set([clazz() for clazz in classes])
                self.assertSetEqual(instances, expected)

    def test_load_classes_complex_path_load(self):
        pkgB_result = {ModuleB3(), ModuleB2(), CustomModuleB1()}
        test_cases = (
            ("../packageA/packageB", None, pkgB_result),
            ("..packageA.packageB", None, pkgB_result),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                classes = self.loader.load_classes(pkg_name, exclude)
                instances = set([clazz() for clazz in classes])
                self.assertSetEqual(instances, expected)

    def test_load_classes_partial_order(self):
        # Only ModuleA1 has order.
        pkgA_result = (ModuleA2(), ModuleA3(), ModuleA1())
        test_cases = (
            ("../packageA", None, pkgA_result),
            ("../packageA/", None, pkgA_result),
            ("..packageA", None, pkgA_result),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                classes = self.loader.load_classes(pkg_name, exclude)
                instances = [clazz() for clazz in classes]
                if not instances[0] == expected[0]:
                    self.fail()
                self.assertSetEqual(set(instances[1:]), set(expected[1:]))

    def test_load_classes_no_order(self):
        # Module1 has other python package.
        basepkg_result = {Module3(), Module1()}
        test_cases = (
            (".", None, basepkg_result),
            ("", None, basepkg_result),
            ("/", None, basepkg_result),
            ("./", None, basepkg_result),
            ("./", ("module_3", "module_2"), {Module1()}),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                classes = self.loader.load_classes(pkg_name, exclude)
                instances = set([clazz() for clazz in classes])
                self.assertSetEqual(instances, expected)

    def test_load_classes_order(self):
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
                classes = self.loader.load_classes(pkg_name, exclude)
                instances = tuple([clazz() for clazz in classes])
                self.assertTupleEqual(instances, expected)

    def test_load_classes_raise_error(self):
        test_cases = (
            ("./nonepackage", None),
            (".", 123),
            (".", [1, 2, 3]),
        )
        for pkg_name, exclude in test_cases:
            with self.assertRaises(Exception):
                self.loader.load_classes(pkg_name, exclude)

    def test_load_classes_recursive(self):
        pkgA_result = {ModuleA2(), ModuleA3(), ModuleA1()}
        pkgB_result = {ModuleB3(), ModuleB2(), CustomModuleB1()}
        test_cases = (
            ("../packageA", False, pkgA_result),
            # expected packageA is ordered, B is random.
            ("../packageA", True, pkgA_result | pkgB_result),
        )
        for pkg_name, recursive, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, recursive=recursive):
                classes = self.loader.load_classes(pkg_name, recursive=recursive)
                instances = set([clazz() for clazz in classes])
                self.assertSetEqual(instances, expected)

    def test_load_multiple_classes(self):
        pkgD_result = (ModuleD1(), ModuleD2(), ModuleD3(), ModuleD4(), ModuleD5(), ModuleD6())
        test_cases = (
            ("packageD", pkgD_result),
        )
        for pkg_name, expected in test_cases:
            with self.subTest(pkg_name=pkg_name):
                classes = self.loader.load_classes(pkg_name)
                instances = tuple([clazz() for clazz in classes])
                self.assertTupleEqual(instances, expected)


if __name__ == '__main__':
    unittest.main()
