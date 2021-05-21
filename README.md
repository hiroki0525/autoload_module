# autoload_module
<a href="https://pypi.org/project/autoload-module" target="_blank">
    <img src="https://img.shields.io/pypi/v/autoload-module?color=%2334D058&label=pypi%20package" alt="autoload-module version">
</a>
<img src="https://img.shields.io/badge/license-MIT-blue.svg?style=flat" alt="MIT License image">

This library will give you comfortable Python metaprogramming.  
The following is a plain example.

- Directory
```
project/
 ├ example.py
 └ validator/
   ├ validator_a.py
   ├ validator_b.py
   └ validator_c.py
```
- example.py
```python
from autoload.module_loader import ModuleLoader

input = "foo bar baz"
loader = ModuleLoader()

# Automatically import modules and return class objects
validator_classes = loader.load_classes("validator")
try:
    # initialize and execute method
    [clazz().validate(input) for clazz in validator_classes]
except:
    print("input is invalid!!")
```
## Install
```
pip install autoload-module
```
## Usage
### Constructor
```
ModuleLoader([base_path])
```
The ModuleLoader can be generated with no parameters.
In that case, the instance has the absolute path where
it was initialized.  
- Directory
```
/usr/local/src/project/
  ├ example.py
  └ validator/
    ├ validator_a.py
    ├ validator_b.py
    └ validator_c.py
```
- example.py
```python
from autoload.module_loader import ModuleLoader

# The instance has '/usr/local/src/project/'
loader = ModuleLoader()

# load modules in the directory; '/usr/local/src/project/validator/'
validator_classes = loader.load_classes("validator")
```
If you want to change the base path, you must generate the ModuleLoader with an absolute path parameter.
```python
loader = ModuleLoader('/user/local/src/custom')
```
### Methods
#### load_classes
```
load_classes(pkg_name, [excludes, recursive])
```
This method read the Python package and return the tuple of class objects.
- Directory
```
pkg/
 ├ example.py
 ├ __init__.py
 ├ config.yaml
 └ main/
     ├ validator_a.py
     ├ validator_b.py
     ├ validator_c.py
     └ sub/
        ├ validator_d.py
        └ validator_e.py
```
- validator_a.py
```python
class ValidatorA:
    def validate(self):
        print("validateA!!")
```
- example.py
```python
loader = ModuleLoader()

# Automatically read modules without '__init__.py', not py file, and this file.
# return the tuple of ValidateA, ValidatorB, and ValidatorC class objects
validator_classes = loader.load_classes("main")

# initialize and execute method
[clazz().validate() for clazz in validator_classes]
# -> validateA!!
# -> validateB!!
# -> validateC!!
```
You can also load only specific modules using `excludes` variable or `load_config` decorator as below.
```python
# Pattern1: 'excludes'
# 'excludes' is a iterable object like tuple, list.
# You must specify module names in 'excludes'.
validator_classes = loader.load_classes("main", ["validator_a"])

[clazz().validate() for clazz in validator_classes]
# -> validateB!!
# -> validateC!!

# Pattern2: 'load_config'
from autoload.decorator import load_config

@load_config(load=False)
class ValidatorA:
  def validate(self):
    print("validateA!!")

validator_classes = loader.load_classes("main")

[clazz().validate() for clazz in validator_classes]
# -> validateB!!
# -> validateC!!
```
This function will check directory structure recursively if you specify `recursive=True`. 
```python
# 'recursive=False' is default.
# In this case, the loader will also check 'pkg/main/sub/'.
validator_classes = loader.load_classes("main", recursive=True)

[clazz().validate() for clazz in validator_classes]
# -> validateA!!
# -> validateB!!
# -> validateC!!
# -> validateD!!
# -> validateE!!
```
You can specify `pkg_name` as below.
```python
loader.load_classes("main/validator_a.py")
loader.load_classes("main.validator_a")
loader.load_classes("./main/validator_a")
loader.load_classes(".main.validator_a")
loader.load_classes("main.sub.validator_d")
loader.load_classes("./main/sub/validator_d")
loader.load_classes("../otherpkg")
loader.load_classes("..otherpkg")
```

#### load_functions
```
load_functions(pkg_name, [excludes, recursive])
```
This method read the Python package and return the tuple of functions.
The usage is the same as `load_classes`.

**NOTE**
- To search class or function, **You must match the name of file, and the one of class or function.**
For example, if you named the file `test_module.py`, you must name the class `TestModule` or the function `test_module`.
When you want to customize their name, use `@load_config` decorator.
    - validator_a.py
    ```python
    from autoload.decorator import load_config
  
    @load_config()
    class CustomValidator:
        def validate(self):
            print("validateA!!")
    ```
- You can also control the order of loaded class objects using `@load_config` decorator.
    - validator_a.py
    ```python
    from autoload.decorator import load_config
  
    # sort in ascending order
    @load_config(order=1)
    class ValidatorA:
        def validate(self):
            print("validateA!!")
    ```
#### load_class
```
load_class(file_name)
```
This method read the Python file and return the class object.
- Directory
```
project/
  ├ example.py
  └ validator.py
```
- validator.py
```python
class Validator:
    def validate(self):
        print("validate!!")
```
- example.py
```python
loader = ModuleLoader()
clazz = loader.load_class("validator")
clazz().validate()
# -> validate!!
```
How to specify `file_name` is the same as that of `load_classes`.

#### load_function
```
load_function(file_name)
```
This method read the Python file and return a function object.
The usage is the same as `load_class`.

## License
Released under the MIT license.