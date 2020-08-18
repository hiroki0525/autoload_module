import importlib
import inspect
import os
import sys


class AutoloadModule:
    op = os.path
    sp = sys.path

    def __init__(self, base_path=None):
        self.__base_path = self.__init_base_url(base_path)

    def load_class(self, file_name):
        target_file = file_name
        if file_name.endswith('.py'):
            target_file = file_name.replace('.py', '')
        fix_path_arr = self.__path_fix(target_file).split('/')
        target_file = fix_path_arr[-2]
        target_path = '/'.join(fix_path_arr[:-2])
        if target_path not in self.sp:
            self.sp.append(target_path)
        module = importlib.import_module(target_file)
        for obj in inspect.getmembers(module, inspect.isclass):
            return obj[1]

    def load_classes(self, pkg_name=None, excludes=None):
        target_dir = self.__path_fix(pkg_name)
        if not self.op.isdir(target_dir):
            raise Exception('Not Found The Directory : {}'.format(target_dir))
        if target_dir not in self.sp:
            self.sp.append(target_dir)
        files = [self.op.splitext(file)[0] for file in os.listdir(target_dir)
                 if file.endswith('.py') and file != '__init__.py' and file != inspect.stack()[1].filename]
        if excludes:
            if not iter(excludes):
                raise TypeError('excludes variable must be iterable.')
            fix_excludes = []
            for exclude in excludes:
                if not isinstance(exclude, str):
                    raise TypeError('The contents of the excludes must all be strings')
                if exclude.endswith('.py'):
                    fix_excludes.append(exclude.replace('.py', ''))
                fix_excludes.append(exclude)
            files = [file for file in files for exclude in fix_excludes if file != exclude]
        classes = []
        for file in files:
            module = importlib.import_module(file)
            for obj in inspect.getmembers(module, inspect.isclass):
                classes.append(obj[1])
        has_order_classes = [clazz for clazz in classes if hasattr(clazz, 'load_order') and clazz.load_order]
        if not has_order_classes:
            return tuple(classes)
        no_has_order_classes = [clazz for clazz in classes if not hasattr(clazz, 'load_order') or not clazz.load_order]
        if not no_has_order_classes:
            return tuple(sorted(has_order_classes))
        ordered_classes = sorted(has_order_classes) + no_has_order_classes
        return tuple(ordered_classes)

    def __init_base_url(self, base_path=None):
        if not base_path:
            return self.op.dirname(inspect.stack()[1].filename)
        if self.__base_path.endswith('/'):
            return self.__base_path[:-1]
        return base_path

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
                # example: .foo
                return self.__base_path + '/' + name[1:] + '/'
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