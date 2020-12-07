import importlib
import inspect
from os import path as os_path
from os import listdir
from sys import path as sys_path

__all__ = (
    "ModuleLoader"
)

_THIS_FILE = os_path.basename(__file__)
_DEFAULT_EXCLUDES = (
    '__init__.py',
    _THIS_FILE,
)
_DECORATOR_ATTR = "load_flg"


def _detect_call_path():
    for path in inspect.stack():
        path_name = path.filename
        filename = os_path.basename(path_name)
        if _THIS_FILE == filename:
            continue
        return path_name


def _init_base_url(base_path=None):
    if base_path is None:
        return _init_base_url(os_path.dirname(_detect_call_path()))
    if base_path == '/':
        return base_path
    if base_path == '':
        return '/'
    if base_path.endswith('/'):
        return base_path[:-1]
    return base_path


class ModuleLoader:
    def __init__(self, base_path=None):
        self.__base_path = _init_base_url(base_path)
        self.__context = None

    @property
    def base_path(self):
        return self.__base_path

    def load_class(self, file_name):
        self.__context = self.Context(self.Context.Type.clazz)
        return self.__load_resource(file_name)

    def load_function(self, file_name):
        self.__context = self.Context(self.Context.Type.func)
        return self.__load_resource(file_name)

    def load_classes(self, pkg_name, excludes=None):
        self.__context = self.Context(self.Context.Type.clazz)
        return self.__load_resources(pkg_name, excludes=excludes)

    def load_functions(self, pkg_name, excludes=None):
        self.__context = self.Context(self.Context.Type.func)
        return self.__load_resources(pkg_name, excludes=excludes, type='function')

    def __path_fix(self, name):
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

    def __load_resource(self, file_name):
        target_file = file_name.replace('.py', '') if file_name.endswith('.py') else file_name
        fix_path_arr = self.__path_fix(target_file).split('/')
        target_file = fix_path_arr[-2]
        target_path = '/'.join(fix_path_arr[:-2])
        if target_path not in sys_path:
            sys_path.append(target_path)
        module = importlib.import_module(target_file)
        comparison = self.__context.draw_comparison(target_file)
        for mod_name, resource in inspect.getmembers(module, self.__context.predicate):
            if hasattr(resource, _DECORATOR_ATTR) and resource.load_flg:
                return resource
            if comparison != mod_name.lower():
                continue
            del self.__context
            return resource

    def __load_resources(self, pkg_name, excludes=None, type='class'):
        target_dir = self.__path_fix(pkg_name)
        if not os_path.isdir(target_dir):
            raise NotADirectoryError('Not Found The Directory : {}'.format(target_dir))
        if target_dir not in sys_path:
            sys_path.append(target_dir)
        files = [os_path.splitext(file)[0] for file in listdir(target_dir) if file.endswith('.py')]
        exclude_files = list(_DEFAULT_EXCLUDES)
        exclude_files.append(os_path.basename(_detect_call_path()))
        if excludes:
            if not iter(excludes):
                raise TypeError('excludes variable must be iterable.')
            for exclude in excludes:
                if not isinstance(exclude, str):
                    raise TypeError('The contents of the excludes must all be strings')
                exclude_files.append(exclude)
        fix_excludes = [exclude.replace('.py', '') for exclude in exclude_files]
        excluded_files = tuple(set(files) - set(fix_excludes))
        classes = []
        for file in excluded_files:
            module = importlib.import_module(file)
            for mod_name, clazz in inspect.getmembers(module, self.__context.predicate):
                if hasattr(clazz, _DECORATOR_ATTR) and clazz.load_flg:
                    classes.append(clazz)
                    break
                if self.__context.draw_comparison(file) != mod_name.lower():
                    continue
                classes.append(clazz)
        del self.__context
        has_order_classes = [clazz for clazz in classes if hasattr(clazz, 'load_order') and clazz.load_order]
        if not has_order_classes:
            return tuple(classes)
        no_has_order_classes = [clazz for clazz in classes if not hasattr(clazz, 'load_order') or not clazz.load_order]
        if not no_has_order_classes:
            return tuple(sorted(has_order_classes, key=lambda clazz: clazz.load_order))
        ordered_classes = sorted(has_order_classes, key=lambda clazz: clazz.load_order) + no_has_order_classes
        return tuple(ordered_classes)

    class Context:
        # Don't use enum because it is not supported under Python 3.4 version
        class Type:
            func = 'function'
            clazz = 'class'

        def __init__(self, type):
            self.__type = type
            if type == self.Type.clazz:
                self.__predicate = inspect.isclass
            else:
                self.__predicate = inspect.isfunction

        @property
        def predicate(self):
            return self.__predicate

        def draw_comparison(self, file):
            if self.__type == self.Type.clazz:
                return "".join(file.split("_")).lower()
            else:
                return file.lower()