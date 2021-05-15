import importlib
import inspect
from enum import Enum, auto
from os import path as os_path
from os import listdir
from sys import path as sys_path
from typing import Optional, Iterable

__all__ = (
    "ModuleLoader"
)


class __Private:
    """
    Private namespace
    """
    THIS_FILE = os_path.basename(__file__)
    DEFAULT_EXCLUDES = (
        '__init__.py',
        THIS_FILE,
    )
    DECORATOR_ATTR = "load_flg"
    EXCLUDE_DIRS = {
        '__pycache__',
    }

    def __new__(cls, *args, **kwargs):
        raise Exception(f"{cls.__name__} can't be initialized.")

    @classmethod
    def detect_call_path(cls):
        this_file = cls.THIS_FILE
        for path in inspect.stack():
            path_name = path.filename
            filename = os_path.basename(path_name)
            if this_file == filename:
                continue
            return path_name

    @classmethod
    def init_base_url(cls, base_path: Optional[str] = None):
        if base_path is None:
            return cls.init_base_url(os_path.dirname(cls.detect_call_path()))
        if base_path == '/':
            return base_path
        if base_path == '':
            return '/'
        if base_path.endswith('/'):
            return base_path[:-1]
        return base_path

    class Context:
        class LoadType(Enum):
            func = auto()
            clazz = auto()

        def __init__(self, type):
            self.__type = type
            self.__predicate = inspect.isclass if type == self.LoadType.clazz else inspect.isfunction

        @property
        def predicate(self):
            return self.__predicate

        def draw_comparison(self, file):
            return "".join(file.split("_")).lower() if self.__type == self.LoadType.clazz else file.lower()


def _access_private():
    return __Private


class ModuleLoader:
    def __init__(self, base_path: Optional[str] = None):
        self.__base_path = _access_private().init_base_url(base_path)
        self.__context = None

    @property
    def base_path(self) -> str:
        return self.__base_path

    def load_class(self, file_name: str):
        private = _access_private()
        self.__context = private.Context(private.Context.LoadType.clazz)
        return self.__load_resource(file_name)

    def load_function(self, file_name: str):
        private = _access_private()
        self.__context = private.Context(private.Context.LoadType.func)
        return self.__load_resource(file_name)

    def load_classes(self, pkg_name: str, excludes: Optional[Iterable[str]] = None, recursive: Optional[bool] = False):
        private = _access_private()
        type = private.Context.LoadType.clazz
        self.__context = private.Context(type)
        return self.__load_resources(pkg_name, excludes=excludes, recursive=recursive, type=type)

    def load_functions(self, pkg_name: str, excludes: Optional[Iterable[str]] = None, recursive: Optional[bool] = False):
        private = _access_private()
        type = private.Context.LoadType.func
        self.__context = private.Context(type)
        return self.__load_resources(pkg_name, excludes=excludes, recursive=recursive, type=type)

    def __path_fix(self, name: str):
        if not name or name == '.' or name == '/' or name == './':
            return self.__base_path
        if name.startswith('/'):
            result_path = self.__base_path + name
            # example: /foo/bar/
            if name.endswith('/'):
                return result_path
            # example: /foo/bar
            return result_path + '/'
        if name.startswith('.'):
            if name[1] != '.':
                if name[1] == '/':
                    result_path = self.__base_path + name[1:]
                    # example: ./foo/
                    if name.endswith('/'):
                        return result_path
                    # example: ./foo
                    return result_path + '/'
                # example: .foo.bar
                return self.__base_path + '/'.join(name.split('.')) + '/'
            level = 0
            path = None
            for i in range(len(name)):
                if i == 0:
                    continue
                if name[i] != '.':
                    break
                path = name[i + 1:]
                level += 1
            base_path_arr = self.__base_path.split('/')
            result_base_path = "/".join(base_path_arr[0:len(base_path_arr) - level])
            if path.startswith('/'):
                if path.endswith('/'):
                    # example: ../foo/
                    return result_base_path + path
                # example: ../foo
                return result_base_path + path + '/'
            # example: ..foo.bar
            path = '/'.join(path.split('.'))
            return result_base_path + '/' + path + '/'
        # example: foo.bar
        path = '/'.join(name.split('.'))
        return self.__base_path + '/' + path + '/'

    def __load_resource(self, file_name: str):
        target_file = file_name.replace('.py', '') if file_name.endswith('.py') else file_name
        fix_path_arr = self.__path_fix(target_file).split('/')
        target_file = fix_path_arr[-2]
        target_path = '/'.join(fix_path_arr[:-2])
        target_path not in sys_path and sys_path.append(target_path)
        module = importlib.import_module(target_file)
        comparison = self.__context.draw_comparison(target_file)
        for mod_name, resource in inspect.getmembers(module, self.__context.predicate):
            if hasattr(resource, _access_private().DECORATOR_ATTR) and resource.load_flg:
                return resource
            if comparison != mod_name.lower():
                continue
            del self.__context
            return resource

    def __load_resources(self, pkg_name: str, excludes: Optional[Iterable[str]] = None, recursive: Optional[bool] = False, type=None):
        target_dir = self.__path_fix(pkg_name)
        if not os_path.isdir(target_dir):
            raise NotADirectoryError('Not Found The Directory : {}'.format(target_dir))
        target_dir not in sys_path and sys_path.append(target_dir)
        files = [os_path.splitext(file)[0] for file in listdir(target_dir) if file.endswith('.py')]
        private = _access_private()
        exclude_files = list(private.DEFAULT_EXCLUDES)
        exclude_files.append(os_path.basename(private.detect_call_path()))
        if excludes:
            if not iter(excludes):
                raise TypeError('excludes variable must be iterable.')
            for exclude in excludes:
                if not isinstance(exclude, str):
                    raise TypeError('The contents of the excludes must all be strings')
                exclude_files.append(exclude)
        fix_excludes = [exclude.replace('.py', '') for exclude in exclude_files]
        excluded_files = tuple(set(files) - set(fix_excludes))
        mods = []
        decorator_attr = private.DECORATOR_ATTR
        for file in excluded_files:
            module = importlib.import_module(file)
            for mod_name, mod in inspect.getmembers(module, self.__context.predicate):
                if hasattr(mod, decorator_attr) and mod.load_flg:
                    mods.append(mod)
                    continue
                if self.__context.draw_comparison(file) == mod_name.lower():
                    if hasattr(mod, decorator_attr) and not mod.load_flg:
                        continue
                    mods.append(mod)
        if recursive is True:
            dirs = [f for f in listdir(target_dir) if os_path.isdir(f'{target_dir}{f}') and f not in private.EXCLUDE_DIRS]
            if len(dirs) > 0:
                for dir in dirs:
                    fix_pkg_name = pkg_name
                    if not fix_pkg_name.endswith('/'):
                        fix_pkg_name += '/'
                    recursive_mods = self.__load_resources(fix_pkg_name + dir, excludes=excludes, recursive=recursive,
                                                           type=type)
                    mods += recursive_mods
        has_order_mods = [mod for mod in mods if hasattr(mod, 'load_order') and mod.load_order]
        if not has_order_mods:
            return tuple(mods)
        no_has_order_mods = [mod for mod in mods if not hasattr(mod, 'load_order') or not mod.load_order]
        if not no_has_order_mods:
            return tuple(sorted(has_order_mods, key=lambda mod: mod.load_order))
        ordered_mods = sorted(has_order_mods, key=lambda mod: mod.load_order) + no_has_order_mods
        return tuple(ordered_mods)
