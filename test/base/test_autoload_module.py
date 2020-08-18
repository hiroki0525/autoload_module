import unittest

from src.autoload_module import AutoloadModule
from test.packageA.test_a1 import TestA1
from test.packageA.test_a2 import TestA2
from test.packageA.test_a3 import TestA3

from test.base.test_3 import Test3

from test.base.test_2 import Test2

from test.base.test_1 import Test1

from test.packageA.packageB.test_b3 import TestB3

from test.packageA.packageB.test_b2 import TestB2

from test.packageA.packageB.test_b1 import TestB1

from test.base.packageC.test_c3 import TestC3

from test.base.packageC.test_c2 import TestC2

from test.base.packageC.test_c1 import TestC1


class TestAutoLoadModule(unittest.TestCase):

    def setUp(self):
        print('setup')
        self.loaders = (
            AutoloadModule(),
        )

    def test_load_class(self):
        test_cases = (
            ("test_1", Test1),
            ("/test_1.py", Test1),
            ("./test_1", Test1),
            ("..packageA.test_a1", TestA1),
            ("../packageA/test_a1", TestA1),
            ("..packageA.packageB.test_b1", TestB1),
            ("../packageA/packageB/test_b1", TestB1),
            ("/packageC/test_c1", TestC1),
            ("./packageC/test_c1", TestC1),
            (".packageC.test_c1", TestC1),
        )
        for file_name, expected in test_cases:
            with self.subTest(file_name=file_name):
                [self.assertEqual(loader.load_class(file_name), expected) for loader in self.loaders]

    def test_load_classes(self):
        basepkg_result = (Test3, Test2, Test1)
        pkgA_result = (TestA2, TestA3, TestA1)
        pkgB_result = (TestB3, TestB2, TestB1)
        pkgC_result = (TestC3, TestC2, TestC1)

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
            ("packageC", [TestC3], (TestC2, TestC1)),
            ("packageC", [TestC3, TestC2], (TestC1)),
            ("packageC", (TestC3, TestC2), (TestC1)),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                [self.assertEqual(loader.load_classes(pkg_name, exclude), expected) for loader in self.loaders]


if __name__ == '__main__':
    unittest.main()
