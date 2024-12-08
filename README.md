# autoload_module

[![PyPI version](https://badge.fury.io/py/autoload-module.svg)](https://badge.fury.io/py/autoload-module)
[![Test](https://github.com/hiroki0525/autoload_module/actions/workflows/test.yml/badge.svg)](https://github.com/hiroki0525/autoload_module/actions/workflows/test.yml)
[![Downloads](https://pepy.tech/badge/autoload-module)](https://pepy.tech/project/autoload-module)
![MIT License image](<%5Bimage_url%5D(https://img.shields.io/badge/license-MIT-blue.svg?style=flat)>)

Get classes and functions from modules simply and efficiently.
The following is a plain example.

▼ Directory

```text
project/
 ├ main.py
 └ pipelines/
   ├ pipeline_a.py
   ├ pipeline_b.py
   └ pipeline_c.py
```

▼ main.py

```py
from autoload import autoload
from functools import reduce

# Automatically import modules and return function objects
pipelines = autoload("pipelines", "function")

initial_value = 1

# Execute functions sequentially
final_result = reduce(lambda acc, func: func(acc), pipelines, initial_value)
```

## Install

```bash
pip install autoload-module
```

## Quick Start

There are only 2 steps. Imagine the following directory structure.

```text
project/
 ├ main.py
 └ functions.py
```

### 1. Set `@loadable` to the class or function you want to import

```py
# functions.py

from autoload import loadable


@loadable
def increment(number: int) -> int:
    return number + 1


@loadable
def decrement(number: int) -> int:
    return number - 1
```

### 2. Set package or module name to `autoload`

```py
# main.py

from autoload import autoload


def main() -> None:
    functions = autoload("pipelines", "function")
    # If you want to get class
    # pipelines = autoload("pipelines", "class")

    # call increment function
    print(functions[0](1))
    # => 2

    # call decrement function
    print(functions[1](1))
    # => 0


if __name__ == "__main__":
    main()
```

## FAQ

### Can I import classes?

Set `"class"` to `autoload` .

▼ Directory

```text
project/
 ├ main.py
 └ pipelines.py
```

▼ Code

```py
# pipelines.py

from autoload import loadable


@loadable
class PipelineA:
    pass


@loadable
class PipelineB:
    pass


# main.py
from autoload import autoload

classes = autoload("pipelines", "class")
```

### Can nested packages be loaded?

Set `"recursive=True"` to `autoload` .

▼ Directory

```text
project/
 ├ main.py
 └ main_package/
   ├ module_a.py
   └ sub_package/
     ├ module_b.py
     └ module_c.py
```

▼ Code

```py
# module_a.py
@loadable
def module_a_function() -> None:
    pass


# module_b.py
@loadable
def module_b_function() -> None:
    pass


# module_c.py
@loadable
def module_c_function() -> None:
    pass


# main.py
# only import module_a_function
functions = autoload("main_package", "function")

# import not only module_a_function but also module_b_function and module_c_function
functions = autoload("main_package", "function", recursive=True)
```

### Can the order of loading be controlled?

Set `order` to `@loadable` .

```py
@loadable(order=3)
def function_3() -> None:
    pass


@loadable(order=1)
def function_1() -> None:
    pass


@loadable(order=2)
def function_2() -> None:
    pass


# main.py
# The order of `functions` is function_1, function_2 and function_3.
functions = autoload("package", "function")
```

### Can relative path be specified?

Set `base` to `autoload` .

```py
functions = autoload("..module_a", "function", base="main_package.sub_package")
```

## License

Released under the MIT license.
