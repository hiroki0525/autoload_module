import inspect
from dataclasses import dataclass
from os import path as os_path
from typing import Callable, ClassVar, Iterable, List, Optional, Tuple, Type

from ._context import Context, ContextFactory
from ._globals import Class_Or_Func, DecoratorVal, LoadType
from ._import import ImportableFactory, ImportOption

__all__ = ("ModuleLoader", "ModuleLoaderSetting")

from .exception import LoaderStrictModeError


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


@dataclass(frozen=True)
class ModuleLoaderSetting:
    base_path: Optional[str] = None
    strict: bool = False
    singleton: bool = False


class ModuleLoader:
    _setting: ClassVar[ModuleLoaderSetting] = ModuleLoaderSetting()
    _instance: Optional["ModuleLoader"] = None
    _INSTANCE_VAL_COUNT = 2

    @classmethod
    def get_setting(cls) -> ModuleLoaderSetting:
        return cls._setting

    @classmethod
    def set_setting(
        cls,
        base_path: Optional[str] = None,
        strict: bool = False,
        singleton: bool = False,
    ) -> None:
        cls._setting = ModuleLoaderSetting(base_path, strict, singleton)

    def __new__(cls, *args, **kwargs):
        if cls._setting.singleton is False:
            cls._instance = None
            return super(ModuleLoader, cls).__new__(cls)
        if cls._instance is None:
            cls._instance = super(ModuleLoader, cls).__new__(cls)
            return cls._instance
        if cls._setting.strict is False:
            return cls._instance
        base_path, strict = list(args) + [None] * (cls._INSTANCE_VAL_COUNT - len(args))
        base_path = kwargs.get("base_path") if base_path is None else base_path
        strict = kwargs.get("strict") if strict is None else strict
        if base_path is None:
            global_base_path = cls._setting.base_path
            base_path = (
                _access_private().init_base_url(base_path)
                if global_base_path is None
                else global_base_path
            )
        if strict is None:
            strict = cls._setting.strict
        ci = cls._instance
        if ci.base_path != base_path or ci.strict != strict:
            raise LoaderStrictModeError(
                "Now singleton setting. "
                "You have already initialized object that has some attributes. "
                "Please check constructor variables."
            )
        return cls._instance

    def __init__(self, base_path: Optional[str] = None, strict: Optional[bool] = None):
        """initialize
        :param base_path: Base path for import.
            Defaults to the path where this object was initialized.
        :param strict: If strict is True,
            ModuleLoader strictly try to load a class or function object
            per a Python module on a basis of its name.
        """
        setting = ModuleLoader._setting
        if setting.singleton is True and hasattr(
            self, f"__{self.__class__.__name__}_base_path"
        ):
            return
        global_base_path, global_strict = setting.base_path, setting.strict
        self.__base_path: str = (
            _access_private().init_base_url(base_path)
            if global_base_path is None
            else global_base_path
        )
        self.__strict: bool = global_strict if strict is None else strict

    @property
    def base_path(self) -> str:
        return self.__base_path

    @property
    def strict(self) -> bool:
        return self.__strict

    def load_class(self, file_name: str) -> Type:
        """Import Python module and return class.
        :param file_name: Python file name (Module name).
            You can input relative path like '../example' based on 'base_path'.
        :return: class object defined in the Python file (Module) according to rules.
        """
        return self.__load_resource(file_name, ContextFactory.get(LoadType.clazz))

    def load_function(self, file_name: str) -> Callable:
        """Import Python module and return function.
        :param file_name: Python file name (module name).
            You can input relative path like '../example' based on 'base_path'.
        :return: function object defined in the Python file (Module) according to rules.
        """
        return self.__load_resource(file_name, ContextFactory.get(LoadType.func))

    def load_classes(
        self,
        src: str,
        excludes: Iterable[str] = (),
        recursive: bool = False,
    ) -> Tuple[Type, ...]:
        """Import Python package and return classes.
        :param src: Python package or module name.
            You can input relative path like '../example' based on 'base_path'.
        :param excludes: Python file names you don't want to import in the package.
        :param recursive: If True, import Python package recursively.
        :return: class objects defined in the Python package according to rules.
        """
        return self.__load_resources(
            src,
            excludes=excludes,
            recursive=recursive,
            context=ContextFactory.get(LoadType.clazz),
        )

    def load_functions(
        self,
        src: str,
        excludes: Iterable[str] = (),
        recursive: bool = False,
    ) -> Tuple[Callable, ...]:
        """Import Python package and return functions.
        :param src: Python package or module name.
            You can input relative path like '../example' based on 'base_path'.
        :param excludes: Python file names you don't want to import in the package.
        :param recursive: If True, import Python package recursively.
        :return: function objects defined in the Python package according to rules.
        """
        return self.__load_resources(
            src,
            excludes=excludes,
            recursive=recursive,
            context=ContextFactory.get(LoadType.func),
        )

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

    def __load_resource(self, file_name: str, context: Context) -> Class_Or_Func:
        if file_name is None:
            raise TypeError("'file_name' parameter is required.")
        if not isinstance(file_name, str):
            raise TypeError("file_name variable must be string.")
        fix_path = self.__path_fix(file_name)
        importable = ImportableFactory.get(fix_path, context)
        return importable.import_resources()[0]

    def __load_resources(
        self,
        src: str,
        context: Context,
        excludes: Iterable[str] = (),
        recursive: bool = False,
    ) -> Tuple[Class_Or_Func, ...]:
        if src is None:
            raise TypeError("'src' parameter is required.")
        if not isinstance(src, str):
            raise TypeError("src variable must be string.")
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
        import_option = ImportOption(recursive, exclude_files, self.__strict)
        target_dir = self.__path_fix(src)
        importable = ImportableFactory.get(target_dir, context, import_option)
        mods: List[Class_Or_Func] = importable.import_resources()
        order_attr = DecoratorVal.order.value
        has_order_mods = [
            mod for mod in mods if hasattr(mod, order_attr) and getattr(mod, order_attr)
        ]
        if not has_order_mods:
            return tuple(mods)
        no_has_order_mods = [
            mod
            for mod in mods
            if not hasattr(mod, order_attr) or not getattr(mod, order_attr)
        ]
        if not no_has_order_mods:
            return tuple(sorted(has_order_mods, key=lambda m: getattr(m, order_attr)))
        ordered_mods = (
            sorted(has_order_mods, key=lambda m: getattr(m, order_attr))
            + no_has_order_mods
        )
        return tuple(ordered_mods)
