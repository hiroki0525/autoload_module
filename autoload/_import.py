import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from importlib import import_module
from os import listdir
from os import path as os_path
from sys import path as sys_path
from typing import Any, Callable, Iterable, List, Optional

from ._context import Context
from .exception import LoaderStrictModeError


def _is_module(name: str):
    return name.endswith(".py")


def _exclude_py(path: str) -> str:
    if _is_module(path):
        return path.replace(".py", "")
    return path


def _exclude_ex(file_name: str) -> str:
    return os_path.splitext(file_name)[0]


def _flatten(iterable: Iterable[Any]) -> Iterable[Any]:
    for el in iterable:
        if isinstance(el, Iterable) and not isinstance(el, (str, bytes)):
            yield from _flatten(el)
        else:
            yield el


_DECORATOR_ATTR = "_load_flg"


@dataclass(frozen=True)
class ImportOption:
    recursive: bool = False
    excludes: Iterable[str] = ()
    is_strict: bool = False


class Importable(ABC):
    def __init__(self, path: str, context: Context, option: ImportOption):
        fix_excludes = [_exclude_py(e) for e in option.excludes]
        self._path = _exclude_py(path)
        self._context = context
        self._option = option
        children = self._load_children()
        self._children: List[Importable] = [
            child for child in children if child.get_base_name() not in fix_excludes
        ]

    @property
    def path(self):
        return self._path

    @abstractmethod
    def import_resources(self):
        raise Exception("'import_resources' method is not defined.")

    def get_base_name(self):
        return _exclude_ex(os_path.basename(self._path))

    def get_all_paths(self):
        return [self._path].extend([child.path for child in self._children])

    def get_children_files(self):
        return [child.get_base_name() for child in self._children]

    def has_children(self) -> bool:
        return len(self._children) > 0

    def load_all(self, callback: Callable):
        children_files = self.get_children_files()
        if len(children_files) == 0:
            return
        for file in children_files:
            module = import_module(file)
            callback(file, module)

    def _load_children(self):
        return []


class _Module(Importable):
    def import_resources(self):
        file = self.get_base_name()
        context = self._context
        is_strict = self._option.is_strict
        load_type_name = context.load_type.value
        module = import_module(file)
        target_load_name = context.draw_comparison(file)
        is_found = False
        error = None
        mods = []
        members = inspect.getmembers(module, context.predicate())
        for mod_name, mod in members:
            is_name_match = target_load_name == mod_name
            if hasattr(mod, _DECORATOR_ATTR):
                if not getattr(mod, "_load_flg"):
                    continue
                if is_found:
                    # High priority error
                    error = LoaderStrictModeError(
                        f"Loader can only load a "
                        f"'{target_load_name}' {load_type_name} in {file} module."
                        f"\nPlease check '{mod_name}' in {file} module."
                    )
                    break
                if is_strict and not is_name_match:
                    error = LoaderStrictModeError(
                        f"Loader can't load '{mod_name}' in {file} module."
                        f"\nPlease rename '{target_load_name}' {load_type_name}."
                    )
                    continue
                mods.append(mod)
                if is_strict:
                    if error:
                        # High priority error
                        error = LoaderStrictModeError(
                            f"Loader can only load a "
                            f"'{target_load_name}' {load_type_name} "
                            f"in {file} module."
                        )
                        break
                    is_found = True
                continue
            if not is_name_match:
                continue
            mods.append(mod)
            if is_strict:
                if error:
                    # High priority error
                    error = LoaderStrictModeError(
                        f"Loader can only load a "
                        f"'{target_load_name}' {load_type_name} in {file} module."
                    )
                    break
                is_found = True
        if error is not None:
            raise error
        return mods


class _Package(Importable):
    def import_resources(self):
        return [
            resource
            for child in self._children
            for resource in child.import_resources()
        ]

    def _load_children(self):
        path = self._path
        option = self._option
        children = []
        for file_or_dir in listdir(path):
            if file_or_dir in option.excludes:
                continue
            is_module = _is_module(file_or_dir)
            is_pkg = os_path.isdir(f"{path}/{file_or_dir}")
            if not is_module and not is_pkg:
                continue
            if is_pkg and not option.recursive:
                continue
            fixed_file_or_dir = _exclude_ex(file_or_dir) if is_module else file_or_dir
            children.append(
                ImportableFactory.get(
                    f"{path}/{fixed_file_or_dir}", self._context, option
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
        return _Module(path, *args, **kwargs)
