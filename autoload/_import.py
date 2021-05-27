from importlib import import_module
from os import listdir
from os import path as os_path
from sys import path as sys_path
from typing import Callable, Iterable, List, Optional


def _exclude_py(path: str) -> str:
    if path.endswith(".py"):
        return path.replace(".py", "")
    return path


def _exclude_ex(file_name: str) -> str:
    return os_path.splitext(file_name)[0]


class Importable:
    def __init__(
        self,
        path: str,
        recursive: bool = False,
        excludes: Optional[Iterable[str]] = None,
    ):
        fix_excludes = [_exclude_py(e) for e in excludes]
        self.__path: str = _exclude_py(path)
        self.__recursive = recursive
        children = self._load_children(excludes)
        self.__children: List[Importable] = [
            child for child in children if child.get_base_name() in fix_excludes
        ]

    @property
    def path(self):
        return self.__path

    def get_base_name(self):
        return _exclude_ex(os_path.basename(self.__path))

    def get_all_paths(self):
        return [self.__path].extend([child.path for child in self.__children])

    def get_children_files(self):
        return [child.get_base_name() for child in self.__children]

    def has_children(self) -> bool:
        return len(self.__children) > 0

    def load_all(self, callback: Callable):
        children_files = self.get_children_files()
        if len(children_files) == 0:
            return
        for file in children_files:
            module = import_module(file)
            callback(file, module)

    def _load_children(self, excludes: Optional[Iterable[str]] = None):
        return []


class _Module(Importable):
    pass


class _Package(Importable):
    def _load_children(self, excludes: Optional[Iterable[str]] = None):
        path = self.__path
        recursive = self.__recursive
        children = []
        for file_or_dir in listdir(path):
            if file_or_dir in excludes:
                continue
            if file_or_dir.endswith(".py"):
                children.append(Importable(f"{path}/{_exclude_ex(file_or_dir)}"))
                continue
            children.append(
                _Package(
                    f"{path}/{file_or_dir}/", recursive=recursive, excludes=excludes
                )
            )
        return children


class ImportableFactory:
    @staticmethod
    def get(path: str, *args, **kwargs):
        if os_path.isdir(path):
            if path not in sys_path:
                sys_path.append(path)
            return _Package(path, *args, **kwargs)
        return _Module(path)
