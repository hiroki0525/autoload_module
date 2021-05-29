import inspect
import warnings
from os import path as os_path
from typing import Callable, Iterable, List, Optional, Tuple, Type

from ._context import Context, ContextFactory
from ._globals import Class_Or_Func, LoadType
from ._import import ImportableFactory, ImportOption

__all__ = "ModuleLoader"


class __Private:
    """Private namespace.
    If you do not want to expose, define here as much as possible.
    """

    THIS_FILE = os_path.basename(__file__)
    DEFAULT_EXCLUDES = ("__init__.py", THIS_FILE, "__pycache__")

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
        src: Optional[str] = None,  # Temporary Optional because of pkg_name
        excludes: Iterable[str] = (),
        recursive: bool = False,
        *args,
        **kwargs,
    ) -> Tuple[Type, ...]:
        """Import Python package and return classes.
        :param src: Python package or module name.
            You can input relative path like '../example' based on 'base_path'.
        :param excludes: Python file names you don't want to import in the package.
        :param recursive: If True, import Python package recursively.
        :return: class objects defined in the Python package according to rules.
        """
        pkg_name = kwargs.get("pkg_name")
        if kwargs.get("pkg_name") is not None:
            warnings.warn(
                "'pkg_name' is deprecated. Please use 'src' parameter.", FutureWarning
            )
            src = pkg_name
        if src is None:
            raise TypeError("'src' parameter is required.")
        self.__context = ContextFactory.get(LoadType.clazz)
        return self.__load_resources(src, excludes=excludes, recursive=recursive)

    def load_functions(
        self,
        src: Optional[str] = None,  # Temporary Optional because of pkg_name
        excludes: Iterable[str] = (),
        recursive: bool = False,
        *args,
        **kwargs,
    ) -> Tuple[Callable, ...]:
        """Import Python package and return functions.
        :param src: Python package or module name.
            You can input relative path like '../example' based on 'base_path'.
        :param excludes: Python file names you don't want to import in the package.
        :param recursive: If True, import Python package recursively.
        :return: function objects defined in the Python package according to rules.
        """
        pkg_name = kwargs.get("pkg_name")
        if kwargs.get("pkg_name") is not None:
            warnings.warn(
                "'pkg_name' is deprecated. Please use 'src' parameter.", FutureWarning
            )
            src = pkg_name
        if src is None:
            raise TypeError("'src' parameter is required.")
        self.__context = ContextFactory.get(LoadType.func)
        return self.__load_resources(src, excludes=excludes, recursive=recursive)

    def __path_fix(self, name: str) -> str:
        if not name or name == "." or name == "/" or name == "./":
            return self.__base_path
        if name.startswith("/"):
            result_path = self.__base_path + name
            # example: /foo/bar/
            if name.endswith("/"):
                return result_path[:-1]
            # example: /foo/bar
            return result_path
        if name.startswith("."):
            if name[1] != ".":
                if name[1] == "/":
                    result_path = self.__base_path + name[1:]
                    # example: ./foo/
                    if name.endswith("/"):
                        return result_path[:-1]
                    # example: ./foo
                    return result_path
                # example: .foo.bar
                return self.__base_path + "/".join(name.split("."))
            level = 0
            path = None
            for i in range(len(name)):
                if i == 0:
                    continue
                if name[i] != ".":
                    break
                path = name[i + 1 :]
                level += 1
            if path is not None:
                base_path_arr = self.__base_path.split("/")
                result_base_path = "/".join(
                    base_path_arr[0 : len(base_path_arr) - level]
                )
                if path.startswith("/"):
                    if path.endswith("/"):
                        # example: ../foo/
                        return result_base_path + path[:-1]
                    # example: ../foo
                    return result_base_path + path
                # example: ..foo.bar
                path = "/".join(path.split("."))
                return result_base_path + "/" + path
        # example: foo.bar
        path = "/".join(name.split("."))
        return self.__base_path + "/" + path

    def __load_resource(self, file_name: str) -> Class_Or_Func:
        fix_path = self.__path_fix(file_name)
        importable = ImportableFactory.get(fix_path, self.__context)
        return importable.import_resources()[0]

    def __load_resources(
        self,
        src: str,
        excludes: Iterable[str] = (),
        recursive: bool = False,
    ) -> Tuple[Class_Or_Func, ...]:
        target_dir = self.__path_fix(src)
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
        context = self.__context
        import_option = ImportOption(recursive, exclude_files, self.__strict)
        importable = ImportableFactory.get(target_dir, context, import_option)
        mods: List[Class_Or_Func] = importable.import_resources()
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
