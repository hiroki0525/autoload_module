import inspect
from importlib import import_module
from os import listdir
from os import path as os_path
from sys import path as sys_path
from typing import Any, Callable, Iterable, List, Optional, Tuple, Type, TypeVar

from ._context import Context, ContextFactory
from ._globals import LoadType
from .exception import LoaderStrictModeError

__all__ = "ModuleLoader"


class __Private:
    """Private namespace.
    If you do not want to expose, define here as much as possible.
    """

    THIS_FILE = os_path.basename(__file__)
    DEFAULT_EXCLUDES = (
        "__init__.py",
        THIS_FILE,
    )
    DECORATOR_ATTR = "_load_flg"
    EXCLUDE_DIRS = {
        "__pycache__",
    }

    def __new__(cls, *args, **kwargs):
        raise Exception(f"{cls.__name__} can't be initialized.")

    @classmethod
    def detect_call_path(cls):
        this_file = cls.THIS_FILE
        stack = inspect.stack()
        for path in stack:
            path_name = path.filename
            if this_file == os_path.basename(path_name):
                continue
            return path_name

    @classmethod
    def init_base_url(cls, base_path: Optional[str] = None):
        if base_path is None:
            return cls.init_base_url(os_path.dirname(cls.detect_call_path()))
        if base_path == "/":
            return base_path
        if base_path == "":
            return "/"
        if base_path.endswith("/"):
            return base_path[:-1]
        return base_path


def _access_private():
    return __Private


_T = TypeVar("_T", Type[Any], Callable)


class ModuleLoader:
    def __init__(self, base_path: Optional[str] = None, strict: bool = False):
        """initialize
        :param base_path: Base path for import.
            Defaults to the path where this object was initialized.
        :param strict: If strict is True,
            ModuleLoader strictly try to load a class or function object
            per a Python module on a basis of its name.
        """
        self.__base_path: str = _access_private().init_base_url(base_path)
        self.__context: Context = ContextFactory.get(LoadType.clazz)
        self.__strict: bool = strict

    @property
    def base_path(self) -> str:
        return self.__base_path

    def load_class(self, file_name: str) -> Type:
        """Import Python module and return class.
        :param file_name: Python file name (Module name).
            You can input relative path like '../example' based on 'base_path'.
        :return: class object defined in the Python file (Module) according to rules.
        """
        self.__context = ContextFactory.get(LoadType.clazz)
        return self.__load_resource(file_name)

    def load_function(self, file_name: str) -> Callable:
        """Import Python module and return function.
        :param file_name: Python file name (module name).
            You can input relative path like '../example' based on 'base_path'.
        :return: function object defined in the Python file (Module) according to rules.
        """
        self.__context = ContextFactory.get(LoadType.func)
        return self.__load_resource(file_name)

    def load_classes(
        self,
        pkg_name: str,
        excludes: Optional[Iterable[str]] = None,
        recursive: bool = False,
    ) -> Tuple[Type]:
        """Import Python package and return classes.
        :param pkg_name: Python package name (directory name).
            You can input relative path like '../example' based on 'base_path'.
        :param excludes: Python file names you don't want to import in the package.
        :param recursive: If True, import Python package recursively.
        :return: class objects defined in the Python package according to rules.
        """
        self.__context = ContextFactory.get(LoadType.clazz)
        return self.__load_resources(pkg_name, excludes=excludes, recursive=recursive)

    def load_functions(
        self,
        pkg_name: str,
        excludes: Optional[Iterable[str]] = None,
        recursive: bool = False,
    ) -> Tuple[Callable]:
        """Import Python package and return functions.
        :param pkg_name: Python package name (directory name).
            You can input relative path like '../example' based on 'base_path'.
        :param excludes: Python file names you don't want to import in the package.
        :param recursive: If True, import Python package recursively.
        :return: function objects defined in the Python package according to rules.
        """
        self.__context = ContextFactory.get(LoadType.func)
        return self.__load_resources(pkg_name, excludes=excludes, recursive=recursive)

    def __path_fix(self, name: str) -> str:
        if not name or name == "." or name == "/" or name == "./":
            return self.__base_path
        if name.startswith("/"):
            result_path = self.__base_path + name
            # example: /foo/bar/
            if name.endswith("/"):
                return result_path
            # example: /foo/bar
            return result_path + "/"
        if name.startswith("."):
            if name[1] != ".":
                if name[1] == "/":
                    result_path = self.__base_path + name[1:]
                    # example: ./foo/
                    if name.endswith("/"):
                        return result_path
                    # example: ./foo
                    return result_path + "/"
                # example: .foo.bar
                return self.__base_path + "/".join(name.split(".")) + "/"
            level = 0
            path = None
            for i in range(len(name)):
                if i == 0:
                    continue
                if name[i] != ".":
                    break
                path = name[i + 1 :]
                level += 1
            # TODO: Error Handling
            if path is not None:
                base_path_arr = self.__base_path.split("/")
                result_base_path = "/".join(
                    base_path_arr[0 : len(base_path_arr) - level]
                )
                if path.startswith("/"):
                    if path.endswith("/"):
                        # example: ../foo/
                        return result_base_path + path
                    # example: ../foo
                    return result_base_path + path + "/"
                # example: ..foo.bar
                path = "/".join(path.split("."))
                return result_base_path + "/" + path + "/"
        # example: foo.bar
        path = "/".join(name.split("."))
        return self.__base_path + "/" + path + "/"

    def __load_resource(self, file_name: str) -> _T:
        target_file = (
            file_name.replace(".py", "") if file_name.endswith(".py") else file_name
        )
        fix_path_arr = self.__path_fix(target_file).split("/")
        target_file = fix_path_arr[-2]
        target_path = "/".join(fix_path_arr[:-2])
        if target_path not in sys_path:
            sys_path.append(target_path)
        module = import_module(target_file)
        context = self.__context
        comparison = context.draw_comparison(target_file)
        for mod_name, resource in inspect.getmembers(module, context.predicate()):
            if hasattr(resource, _access_private().DECORATOR_ATTR) and getattr(
                resource, "_load_flg"
            ):
                return resource
            if comparison != mod_name:
                continue
            return resource

    def __load_resources(
        self,
        pkg_name: str,
        excludes: Optional[Iterable[str]] = None,
        recursive: Optional[bool] = False,
    ) -> Tuple[_T]:
        target_dir = self.__path_fix(pkg_name)
        if not os_path.isdir(target_dir):
            raise NotADirectoryError(f"Not Found The Directory : {target_dir}")
        if target_dir not in sys_path:
            sys_path.append(target_dir)
        files = [
            os_path.splitext(file)[0]
            for file in listdir(target_dir)
            if file.endswith(".py")
        ]
        private = _access_private()
        exclude_files = list(private.DEFAULT_EXCLUDES)
        exclude_files.append(os_path.basename(private.detect_call_path()))
        if excludes:
            if not iter(excludes):
                raise TypeError("excludes variable must be iterable.")
            for exclude in excludes:
                if not isinstance(exclude, str):
                    raise TypeError("The contents of the excludes must all be strings")
                exclude_files.append(exclude)
        fix_excludes = [exclude.replace(".py", "") for exclude in exclude_files]
        excluded_files = set(files) - set(fix_excludes)
        mods: List[_T] = []
        decorator_attr = private.DECORATOR_ATTR
        context = self.__context
        is_strict = self.__strict
        load_type_name = context.load_type.value
        for file in excluded_files:
            module = import_module(file)
            target_load_name = context.draw_comparison(file)
            is_found = False
            error = None
            members = inspect.getmembers(module, context.predicate())
            for mod_name, mod in members:
                is_name_match = target_load_name == mod_name
                if hasattr(mod, decorator_attr):
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
        if recursive:
            dirs = [
                f
                for f in listdir(target_dir)
                if os_path.isdir(f"{target_dir}{f}") and f not in private.EXCLUDE_DIRS
            ]
            if len(dirs) > 0:
                for dir in dirs:
                    fix_pkg_name = pkg_name
                    if not fix_pkg_name.endswith("/"):
                        fix_pkg_name += "/"
                    recursive_mods = self.__load_resources(
                        fix_pkg_name + dir,
                        excludes=excludes,
                        recursive=recursive,
                    )
                    mods += recursive_mods
        has_order_mods = [
            mod
            for mod in mods
            if hasattr(mod, "_load_order") and getattr(mod, "_load_order")
        ]
        if not has_order_mods:
            return tuple(mods)
        no_has_order_mods = [
            mod
            for mod in mods
            if not hasattr(mod, "_load_order") or not getattr(mod, "_load_order")
        ]
        if not no_has_order_mods:
            return tuple(
                sorted(has_order_mods, key=lambda m: getattr(m, "_load_order"))
            )
        ordered_mods = (
            sorted(has_order_mods, key=lambda m: getattr(m, "_load_order"))
            + no_has_order_mods
        )
        return tuple(ordered_mods)
