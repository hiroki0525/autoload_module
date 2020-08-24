from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='autoload_module',
    description='Python Autoload Module',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT License",
    version='0.1.2',
    url='https://github.com/hiroki0525/autoload_module',
    author='Hiroki Miyaji',
    author_email='nukoprogramming@gmail.com',
    packages=find_packages(exclude=['test']),
)