import sys
import unittest
from pathlib import Path

from tests.clazz.base.packageD.module_d1 import ModuleD1, ModuleD2, ModuleD3
from tests.clazz.base.packageD.module_d2 import ModuleD4, ModuleD5
from tests.clazz.base.packageD.module_d3 import ModuleD6

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "autoload"))

from autoload import ModuleLoader
from autoload.exception import LoaderStrictModeError
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
        self.loader = ModuleLoader()

    def tearDown(self) -> None:
        ModuleLoader.set_setting()

    def test_global_setting(self):
        default = self.loader
        test_cases = (
            ((), (default.base_path, default.strict)),
            (('/',), ('/', default.strict)),
            ((None, True), (default.base_path, True)),
            (('/', False), ('/', False)),
        )
        for setting, expected in test_cases:
            with self.subTest(setting=setting):
                ModuleLoader.set_setting(*setting)
                test_loader = ModuleLoader()
                test_loader2 = ModuleLoader()
                self.assertTupleEqual((test_loader.base_path, test_loader.strict), expected)
                self.assertTupleEqual((test_loader2.base_path, test_loader2.strict), expected)

    def test_switch_global_setting(self):
        ModuleLoader.set_setting(singleton=True)
        singleton_a = ModuleLoader()
        singleton_b = ModuleLoader()
        ModuleLoader.set_setting()
        no_singleton_a = ModuleLoader()
        no_singleton_b = ModuleLoader()
        self.assertIs(singleton_a, singleton_b)
        self.assertIsNot(singleton_a, no_singleton_a)
        self.assertIsNot(no_singleton_a, no_singleton_b)

    def test_singleton(self):
        ModuleLoader.set_setting(singleton=True)
        test_cases = (
            (ModuleLoader(), ModuleLoader()),
            (ModuleLoader('/test', strict=True), ModuleLoader()),
        )
        for instance, expected in test_cases:
            with self.subTest(instance=instance):
                self.assertIs(instance, expected)
                self.assertEqual(instance.base_path, expected.base_path)
                self.assertEqual(instance.strict, expected.strict)

    def test_singleton_with_strict(self):
        ModuleLoader.set_setting(singleton=True, strict=True)
        singleton = ModuleLoader()
        test_cases = (
            ('/test',),
            ('/test', {"strict": False},),
            ({"strict": True},),
        )
        for args in test_cases:
            with self.subTest(args=args):
                with self.assertRaises(LoaderStrictModeError, msg="Now singleton setting."):
                    ModuleLoader(*args)

    def test_not_singleton(self):
        test_cases = (
            (ModuleLoader(), ModuleLoader(), False),
            (ModuleLoader('/test', strict=True), ModuleLoader(), True),
        )
        for instance, expected, optional in test_cases:
            with self.subTest(instance=instance):
                self.assertIsNot(instance, expected)
                if optional:
                    self.assertNotEqual(instance.base_path, expected.base_path)
                    self.assertNotEqual(instance.strict, expected.strict)

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

    def test_load_classes_by_module(self):
        test_cases = (
            ("module_1", {Module1()}),
            (".packageD.not_load", set()),
            (".packageD.module_d1", {ModuleD1(), ModuleD2(), ModuleD3()}),
            (".packageD.module_d2", {ModuleD4(), ModuleD5()}),
        )
        for pkg_name, expected in test_cases:
            with self.subTest(pkg_name=pkg_name):
                classes = self.loader.load_classes(pkg_name)
                instances = set([clazz() for clazz in classes])
                self.assertSetEqual(instances, expected)

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
        for pkg_name, excludes, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, excludes=excludes):
                classes = self.loader.load_classes(pkg_name=pkg_name, excludes=excludes)
                instances = set([clazz() for clazz in classes])
                self.assertSetEqual(instances, expected)

    def test_load_classes_complex_path_load(self):
        pkgB_result = {ModuleB3(), ModuleB2(), CustomModuleB1()}
        test_cases = (
            ("../packageA/packageB", pkgB_result),
            ("..packageA.packageB", pkgB_result),
        )
        for pkg_name, expected in test_cases:
            with self.subTest(pkg_name=pkg_name):
                classes = self.loader.load_classes(pkg_name)
                instances = set([clazz() for clazz in classes])
                self.assertSetEqual(instances, expected)

    def test_load_classes_partial_order(self):
        # Only ModuleA1 has order.
        pkgA_result = (ModuleA2(), ModuleA3(), ModuleA1())
        test_cases = (
            ("../packageA", pkgA_result),
            ("../packageA/", pkgA_result),
            ("..packageA", pkgA_result),
        )
        for pkg_name, expected in test_cases:
            with self.subTest(pkg_name=pkg_name):
                classes = self.loader.load_classes(pkg_name)
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

    def test_strict_mode(self):
        self.loader = ModuleLoader(strict=True)
        self.test_load_classes_exclude()
        self.test_load_classes_partial_order()
        self.test_load_classes_no_order()
        self.test_load_classes_order()

    def test_strict_mode_raise_error(self):
        self.loader = ModuleLoader(strict=True)
        test_cases = (
            ("packageD", "Loader can't load 'ModuleD6' in module_d3 module.",),
            ("packageD.module_d1", "Loader can only load a 'ModuleD1' class in module_d1 module.",)
        )
        for pkg_name, msg in test_cases:
            with self.subTest(pkg_name=pkg_name):
                with self.assertRaises(LoaderStrictModeError):
                    self.loader.load_classes(pkg_name)


if __name__ == '__main__':
    unittest.main()
