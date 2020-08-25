from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='autoload_module',
    description='Python Autoload Module',
    long_description=long_description,
    keywords=(
        'python',
        'import',
        'autoload',
        'autoload_module',
        'dynamic import',
        'metaprogramming',
    ),
    classifiers=(
        'Topic :: Software Development :: Libraries',
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ),
    long_description_content_type="text/markdown",
    license="MIT License",
    version='1.0.1',
    url='https://github.com/hiroki0525/autoload_module',
    author='Hiroki Miyaji',
    author_email='nukoprogramming@gmail.com',
    py_modules = ['autoload.module_loader', 'autoload.decorator']
)