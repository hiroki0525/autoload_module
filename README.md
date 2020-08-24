# autoload_module
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
from src.autoload_module import AutoloadModule

input = "foo bar baz"
loader = AutoloadModule()
validator_classes = loader.load_classes("validator")
try:
    [clazz().validate(input) for clazz in validator_classes]
except:
    print("input is invalid!!")
```
## Install
```
pip install autoload_module
```
## Usage
### Constructor
```
AutoloadModule([base_path])
```
The AutoloadModule can be generated with no parameters.
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
from src.autoload_module import AutoloadModule

# The instance has '/usr/local/src/project/'
loader = AutoloadModule()

# load modules in the directory; '/usr/local/src/project/validator/'
validator_classes = loader.load_classes("validator")
```
If you want to change the base path, you must generate the AutoloadModule with an absolute path parameter.
```python
loader = AutoloadModule('/user/local/src/custom')
```
### Methods
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
loader = AutoloadModule()
clazz = loader.load_class("validator")
clazz().validate()
# -> validate!!
```
You can specify `file_name` as below.
```python
loader.load_class("validator.py")
loader.load_class(".validator")
loader.load_class("/validator")
loader.load_class("./validator")

# relative path
loader.load_class("..packageA.validator")
loader.load_class("../packageA/validator")
```
#### load_classes
```
load_classes(pkg_name, [excludes])
```
This method read the Python package and return the tuple of class objects.
- Directory
```
project/
 ├ __init__.py
 ├ config.yaml
 ├ example.py
 ├ validator_a.py
 ├ validator_b.py
 └ validator_c.py
```
- validator_a.py
```python
class ValidatorA:
    def validate(self):
        print("validateA!!")
```
- example.py
```python
loader = AutoloadModule()

# Automatically read modules without '__init__.py', not py file, and this file.
# return the tuple of ValidateA, ValidatorB, and ValidatorC class objects
validator_classes = loader.load_classes("project")

# initialize and execute method
[clazz().validate() for clazz in validator_classes]
# -> validateA!!
# -> validateB!!
# -> validateC!!
```
**NOTE**
- To search class, **You must match the file name and class name.**
For example, if you named the file `test_module.py`, you must named the class `TestModule`.
When you want to custimize the class name, use `@load_config` decorator as below.
    - validator_a.py
    ```python
    @load_config(module_name="validator_a")
    class CustomValidator:
        def validate(self):
            print("validateA!!")
    ```
- You can also control the order of loaded class objects using `@load_config` decorator.
    - validator_a.py
    ```python
    # sort in ascending order
    @load_config(order=1)
    class ValidatorA:
        def validate(self):
            print("validateA!!")
    ```

## License
Released under the MIT license.