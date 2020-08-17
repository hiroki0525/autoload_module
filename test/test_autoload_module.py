import unittest

from src.autoload_module import AutoloadModule
from test.packageA.test_a import TestA
from test.packageA.test_b import TestB
from test.packageA.test_c import TestC


class TestAutoLoadModule(unittest.TestCase):

    def setUp(self):
        print('setup')
        # TODO: 他を加える
        self.loaders = (
            AutoloadModule(),
        )

    def test_load_class(self):
        test_cases = (
            ("test_a", TestA),
            ("/test_a", TestA),
            (".test_a", TestA),
            ("./test_a", TestA),
            ("../test_a", TestA),
            ("..test_a", TestA),
            ("/packageA/test_a", TestA),
            ("./packageA/test_a", TestA),
            ("../packageA/test_a", TestA),
            ("test_a.py", TestA),
        )
        for file_name, expected in test_cases:
            with self.subTest(file_name=file_name):
                [self.assertEqual(loader.load_class(file_name), expected) for loader in self.loaders]

    def test_load_classes(self):
        test_cases = (
            ("packageA", None, (TestA, TestB, TestC)),
            ("/test_a", None, (TestA, TestB, TestC)),
            (".test_a", None, (TestA, TestB, TestC)),
            ("./test_a", None, (TestA, TestB, TestC)),
            ("../test_a", None, (TestA, TestB, TestC)),
            ("..test_a", None, (TestA, TestB, TestC)),
            ("/packageA/test_a", [], (TestA, TestB, TestC)),
            ("./packageA/test_a", [TestA], (TestB, TestC)),
            ("../packageA/test_a", [TestA, TestB], (TestC)),
            ("../packageA/test_a", (TestA, TestB), (TestC)),
        )
        for pkg_name, exclude, expected in test_cases:
            with self.subTest(pkg_name=pkg_name, exclude=exclude):
                [self.assertEqual(loader.load_classes(pkg_name, exclude), expected) for loader in self.loaders]


if __name__ == '__main__':
    unittest.main()
