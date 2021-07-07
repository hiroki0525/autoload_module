import inspect
from abc import ABC, abstractmethod
from dataclasses import dataclass
from importlib import import_module
from os import listdir
from os import path as os_path
from sys import path as sys_path
from typing import Iterable, List

from ._context import Context
from ._globals import Class_Or_Func, DecoratorVal
from .exception import LoaderStrictModeError


def _is_module(name: str) -> bool:
    return name.endswith(".py")


def _exclude_py(path: str) -> str:
    if _is_module(path):
        return path.replace(".py", "")
    return path


def _exclude_ex(file_name: str) -> str:
    return os_path.splitext(file_name)[0]


@dataclass(frozen=True)
class ImportOption:
    recursive: bool = False
    excludes: Iterable[str] = ()
    is_strict: bool = False


default_option = ImportOption()


class Importable(ABC):
    def __init__(
        self, path: str, context: Context, option: ImportOption = default_option
    ):
        self._path = _exclude_py(path)
        self._context = context
        self._option = option
        children = self._load_children()
        fix_excludes = [_exclude_py(e) for e in option.excludes]
        self._children: List[Importable] = [
            child for child in children if child.get_base_name() not in fix_excludes
        ]

    @abstractmethod
    def import_resources(self) -> List[Class_Or_Func]:
        raise Exception("'import_resources' method is not defined.")

    def get_base_name(self) -> str:
        return _exclude_ex(os_path.basename(self._path))

    def _load_children(self) -> List["Importable"]:
        return []


class _Module(Importable):
    def import_resources(self) -> List[Class_Or_Func]:
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
        load_flg_attr = DecoratorVal.flg.value
        for mod_name, mod in members:
            is_name_match = target_load_name == mod_name
            if hasattr(mod, load_flg_attr):
                if not getattr(mod, load_flg_attr):
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
    def import_resources(self) -> List[Class_Or_Func]:
        return [
            resource
            for child in self._children
            for resource in child.import_resources()
        ]

    def _load_children(self) -> List[Importable]:
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
    def get(path: str, *args, **kwargs) -> Importable:
        is_dir = os_path.isdir(path)
        fixed_path = path if is_dir else "/".join(path.split("/")[:-1])
        if fixed_path not in sys_path:
            sys_path.append(fixed_path)
        if is_dir:
            return _Package(path, *args, **kwargs)
        return _Module(path, *args, **kwargs)
