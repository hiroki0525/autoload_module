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

# '__init__.py'やpyファイル以外のファイル(yamlなど)、このファイルを除いて自動的に読み込みます
# 戻り値は（<class ValidateA>, <class ValidatorB>, <class ValidatorC>）です
validator_classes = loader.load_classes("main")

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
validator_classes = loader.load_classes("main", ["validator_a", "validator_b"])

[clazz().validate() for clazz in validator_classes]
# -> validateC!!
```
`recursive=True`を指定するとディレクトリ構造も再起的にチェックします。 
```python
# recursive=Falseがデフォルト。
# サブディレクトリであるsub/も読み込まれます。
validator_classes = loader.load_classes("main", recursive=True)
```
なお、パッケージ名は次のように指定できます。
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
load_functions(pkg_name, [excludes])
```
引数で与えられたパッケージ名から配下のモジュールをimportし、関数オブジェクトのタプルを返却します。
使い方は `load_classes` と同じです。

**NOTE**
- クラスや関数を検索するために, **モジュール名とクラス名また関数名を一致させてください.**
例えば, もし `test_module.py` と命名したのであれば, クラス名は `TestModule` 、関数名は `test_module` にしてください。
クラス名や関数名をカスタマイズしたい場合は, `@load_config` デコレータで `load=True` を指定してください。
    - validator_a.py
    ```python
    from autoload.decorator import load_config
  
    @load_config(load=True)
    class CustomValidator:
        def validate(self):
            print("validateA!!")
    ```
- 返却されるクラスオブジェクトに順番を持たせたいなら、同じく `@load_config` デコレータを使ってください。
    - validator_a.py
    ```python
    from autoload.decorator import load_config
  
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

```
load_function(file_name)
```
Pythonファイルをimportして関数オブジェクトを返却します。
使い方は `load_class` と同じです。

## License
Released under the MIT license.