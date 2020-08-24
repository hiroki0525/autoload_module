# autoload_module
This library will give you comfortable Python metaprogramming.  
The following is a plain example.

Directory
```
project/
 ├ example.py
 └ validator/
   ├ validator_a.py
   ├ validator_b.py
   └ validator_c.py
```
example.py
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

## License
Released under the MIT license.