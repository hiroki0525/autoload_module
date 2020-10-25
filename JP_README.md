# autoload_module
このライブラリは快適なメタプログラミングをあなたに提供します。  
簡単な例を挙げます。
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

# 自動的にvalidator配下のモジュールをimportし、クラスオブジェクトのリストを返却
validator_classes = loader.load_classes("validator")
try:
    # インスタンス化してメソッドを実行
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
ModuleLoader([base_path])
```
コンストラクターは引数なしで実行できます。
その場合は、ModuleLoaderがインスタンス化されたファイルのパスが内部的に保持されます。  
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

# loaderの内部的で '/usr/local/src/project/' が保持されます
loader = ModuleLoader()

# 内部的に保持されたパスを基準に読み込みます。この場合は '/usr/local/src/project/validator/' です
validator_classes = loader.load_classes("validator")
```
もし基準となるパスを変更したい場合は、コンストラクタの引数でパスを渡してください。
```python
loader = ModuleLoader('/user/local/src/custom')
```
### Methods
#### load_classes
```
load_classes(pkg_name, [excludes])
```
引数で与えられたパッケージ名から配下のモジュールをimportし、クラスオブジェクトのタプルを返却します。
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
loader = ModuleLoader()

# '__init__.py'やpyファイル以外のファイル(yamlなど)、このファイルを除いて自動的に読み込みます
# 戻り値は（<class ValidateA>, <class ValidatorB>, <class ValidatorC>）です
validator_classes = loader.load_classes("project")

# インスタンス化してメソッド実行
[clazz().validate() for clazz in validator_classes]
# -> validateA!!
# -> validateB!!
# -> validateC!!
```
特定のモジュールを読み込みから外したい場合は `excludes` を使ってください。
```python
# 'excludes' は iterable なオブジェクトを指定します
# 'excludes' のリスト内はモジュール名を指定してください
validator_classes = loader.load_classes("project", ["validator_a", "validator_b"])

[clazz().validate() for clazz in validator_classes]
# -> validateC!!
```
なお、パッケージ名は次のように指定できます。
```python
loader.load_classes("validator.py")
loader.load_classes(".validator")
loader.load_classes("/validator")
loader.load_classes("./validator")

# 相対パス
loader.load_classes("..packageA.validator")
loader.load_classes("../packageA/validator")
```

**NOTE**
- クラスを検索するために, **モジュール名とクラス名を一致させてください.**
例えば, もし `test_module.py` と命名したのであれば, クラス名は `TestModule` にしてください。
クラス名をカスタマイズしたい場合は, `@load_config` デコレータで `load=True` を指定してください。
    - validator_a.py
    ```python
    @load_config(load=True)
    class CustomValidator:
        def validate(self):
            print("validateA!!")
    ```
- 返却されるクラスオブジェクトに順番を持たせたいなら、同じく `@load_config` デコレータを使ってください。
    - validator_a.py
    ```python
    # 昇順でソートされます
    @load_config(order=1)
    class ValidatorA:
        def validate(self):
            print("validateA!!")
    ```
#### load_class
```
load_class(file_name)
```
Pythonファイルをimportしてクラスオブジェクトを返却します。
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
`file_name`の指定方法は `load_classes` と同じです。

## License
Released under the MIT license.