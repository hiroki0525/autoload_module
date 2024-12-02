"""Module for loading classes and functions from Python modules and packages.

based on given settings.
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, ClassVar, cast

if TYPE_CHECKING:
    from collections.abc import Iterable

from typing_extensions import Self

from ._context import Context, ContextFactory
from ._globals import Class_Or_Func, DecoratorVal, LoadType
from ._import import Importable, ImportOption

__all__ = ("ModuleLoader", "ModuleLoaderSetting")

from pathlib import Path

from .exception import LoaderStrictModeError

__THIS_FILE = Path(__file__).name
_DEFAULT_EXCLUDES = ("__init__.py", __THIS_FILE, "__pycache__")


def _detect_call_path() -> str | None:
    this_file = __THIS_FILE
    stack = inspect.stack()
    for path in stack:
        path_name = path.filename
        if this_file == Path(path_name).name:
            continue
        return path_name
    return None


def _init_base_url(base_path: str | None = None) -> str:
    if base_path is None:
        call_path = _detect_call_path()
        if call_path is None:
            msg = "Call path could not be detected."
            raise ValueError(msg)
        return _init_base_url(str(Path(call_path).parent))
    if base_path == "/":
        return base_path
    if base_path == "":
        return "/"
    if base_path.endswith("/"):
        return base_path[:-1]
    return base_path


@dataclass(frozen=True)
class ModuleLoaderSetting:
    """Settings for the ModuleLoader."""

    base_path: str | None = None
    strict: bool = False
    singleton: bool = False


class ModuleLoader:
    """Class responsible for loading modules, classes, and functions.

    based on given settings.
    """

    _setting: ClassVar[ModuleLoaderSetting] = ModuleLoaderSetting()
    _instance: Self | None = None
    _INSTANCE_VAL_COUNT = 2

    @classmethod
    def get_setting(cls) -> ModuleLoaderSetting:
        """Get the current settings of the ModuleLoader."""
        return cls._setting

    @classmethod
    def set_setting(
        cls,
        base_path: str | None = None,
        strict: bool = False,
        singleton: bool = False,
    ) -> None:
        """Set the settings for the ModuleLoader.

        :param base_path: Base path for import.
        :param strict: If True, ModuleLoader strictly tries to load a class or
            function object per a Python module based on its name.
        :param singleton: If True, ensures only one instance of ModuleLoader is created.
        """
        cls._setting = ModuleLoaderSetting(base_path, strict, singleton)

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:  # noqa: ANN401
        """Create and return a new instance of ModuleLoader."""
        if cls._setting.singleton is False:
            cls._instance = None
            return super().__new__(cls)
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            return cls._instance
        if cls._setting.strict is False:
            return cls._instance
        base_path, strict = list(args) + [None] * (cls._INSTANCE_VAL_COUNT - len(args))
        base_path = kwargs.get("base_path") if base_path is None else base_path
        strict = kwargs.get("strict") if strict is None else strict
        if base_path is None:
            global_base_path = cls._setting.base_path
            base_path = (
                _init_base_url(base_path)
                if global_base_path is None
                else global_base_path
            )
        if strict is None:
            strict = cls._setting.strict
        ci = cls._instance
        if ci.base_path != base_path or ci.strict != strict:
            error_message = (
                "Now singleton setting. "
                "You have already initialized object that has some attributes. "
                "Please check constructor variables."
            )
            raise LoaderStrictModeError(error_message)
        return cls._instance

    def __init__(
        self,
        base_path: str | None = None,
        strict: bool | None = None,
    ) -> None:
        """Initialize.

        :param base_path: Base path for import.
            Defaults to the path where this object was initialized.
        :param strict: If strict is True,
            ModuleLoader strictly try to load a class or function object
            per a Python module on a basis of its name.
        """
        setting = ModuleLoader._setting
        if setting.singleton is True and hasattr(
            self,
            f"__{self.__class__.__name__}_base_path",
        ):
            return
        global_base_path, global_strict = setting.base_path, setting.strict
        self.__base_path: str = (
            _init_base_url(base_path) if global_base_path is None else global_base_path
        )
        self.__strict: bool = global_strict if strict is None else strict

    @property
    def base_path(self) -> str:
        """Return the base path setting."""
        return self.__base_path

    @property
    def strict(self) -> bool:
        """Return the strict mode setting."""
        return self.__strict

    def load_class(self, file_name: str) -> type:
        """Import Python module and return class.

        :param file_name: Python file name (Module name).
            You can input relative path like '../example' based on 'base_path'.
        :return: class object defined in the Python file (Module) according to rules.
        """
        return cast(
            type,
            self.__load_resource(file_name, ContextFactory.get(LoadType.clazz)),
        )

    def load_function(self, file_name: str) -> Callable:
        """Import Python module and return function.

        :param file_name: Python file name (module name).
            You can input relative path like '../example' based on 'base_path'.
        :return: function object defined in the Python file (Module) according to rules.
        """
        return cast(
            Callable,
            self.__load_resource(file_name, ContextFactory.get(LoadType.func)),
        )

    def load_classes(
        self,
        src: str,
        excludes: Iterable[str] = (),
        recursive: bool = False,
    ) -> tuple[type, ...]:
        """Import Python package and return classes.

        :param src: Python package or module name.
            You can input relative path like '../example' based on 'base_path'.
        :param excludes: Python file names you don't want to import in the package.
        :param recursive: If True, import Python package recursively.
        :return: class objects defined in the Python package according to rules.
        """
        return cast(
            tuple[type, ...],
            self.__load_resources(
                src,
                excludes=excludes,
                recursive=recursive,
                context=ContextFactory.get(LoadType.clazz),
            ),
        )

    def load_functions(
        self,
        src: str,
        excludes: Iterable[str] = (),
        recursive: bool = False,
    ) -> tuple[Callable, ...]:
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

    def __path_fix(self, name: str) -> str:  # noqa: C901, PLR0911, PLR0912
        if not name or name in (".", "/", "./"):
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
                    base_path_arr[0 : len(base_path_arr) - level],
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
        path = "/".join(name.split("."))
        return self.__base_path + "/" + path

    def __load_resource(self, file_name: str, context: Context) -> Class_Or_Func:
        fix_path = self.__path_fix(file_name)
        importable = Importable(fix_path, context)
        return importable.import_resources()[0]

    def __load_resources(
        self,
        src: str,
        context: Context,
        excludes: Iterable[str] = (),
        recursive: bool = False,
    ) -> tuple[Class_Or_Func, ...]:
        exclude_files = list(_DEFAULT_EXCLUDES).copy()
        call_path = _detect_call_path()
        if call_path:
            exclude_files.append(Path(call_path).name)
        if excludes:
            for exclude in excludes:
                exclude_files.append(exclude)
        import_option = ImportOption(recursive, exclude_files, self.__strict)
        target_dir = self.__path_fix(src)
        importable = Importable(target_dir, context, import_option)
        mods: list[Class_Or_Func] = importable.import_resources()
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
