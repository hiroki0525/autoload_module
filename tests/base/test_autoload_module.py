import sys
import unittest
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from src.autoload_module import AutoloadModule
from tests.base.module_1 import Module1
from tests.base.module_2 import Module2
from tests.base.module_3 import Module3
from tests.base.packageC.module_c1 import ModuleC1
from tests.base.packageC.module_c2 import ModuleC2
from tests.base.packageC.module_c3 import ModuleC3
from tests.packageA.module_a1 import ModuleA1
from tests.packageA.module_a2 import ModuleA2
from tests.packageA.module_a3 import ModuleA3
from tests.packageA.packageB.module_b1 import ModuleB1
from tests.packageA.packageB.module_b2 import ModuleB2
from tests.packageA.packageB.module_b3 import ModuleB3


class ModuleAutoLoadModule(unittest.TestCase):

    def setUp(self):
        print('setup')
        self.loaders = (
            AutoloadModule(),
        )

    def test_load_class(self):
        test_cases = (
            ("module_1", Module1),
            ("/module_1.py", Module1),
            ("./module_1", Module1),
            ("..packageA.module_a1", ModuleA1),
            ("../packageA/module_a1", ModuleA1),
            ("..packageA.packageB.module_b1", ModuleB1),
            ("../packageA/packageB/module_b1", ModuleB1),
            ("/packageC/module_c1", ModuleC1),
            ("./packageC/module_c1", ModuleC1),
            (".packageC.module_c1", ModuleC1),
        )
        for file_name, expected in test_cases:
            with self.subTest(file_name=file_name):
                [self.assertEqual(loader.load_class(file_name), expected) for loader in self.loaders]

    def test_load_classes(self):
        basepkg_result = (Module3, Module2, Module1)
        pkgA_result = (ModuleA2, ModuleA3, ModuleA1)
        pkgB_result = (ModuleB3, ModuleB2, ModuleB1)
        pkgC_result = (ModuleC3, ModuleC2, ModuleC1)

        test_cases = (
            (".", None, basepkg_result),
            ("", None, basepkg_result),
            ("/", None, basepkg_result),
            ("./", None, basepkg_result),
            ("../packageA", None, pkgA_result),
            ("../packageA/", None, pkgA_result),
            ("..packageA", None, pkgA_result),
            ("../packageA/packageB", None, pkgB_result),
            ("..packageA.packageB", None, pkgB_result),
            ("packageC", None, pkgC_result),
            (".packageC", None, pkgC_result),
            ("/packageC/", None, pkgC_result),
            ("/packageC", None, pkgC_result),
            ("./packageC", None, pkgC_result),
            ("nopackage", None, ()),
            ("packageC", [], pkgC_result),
            ("packageC", [ModuleC3], (ModuleC2, ModuleC1)),
            ("packageC", [ModuleC3, ModuleC2], (ModuleC1)),
            ("packageC", (ModuleC3, ModuleC2), (ModuleC1)),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                [self.assertTupleEqual(loader.load_classes(pkg_name, exclude), expected) for loader in self.loaders]


if __name__ == '__main__':
    unittest.main()
