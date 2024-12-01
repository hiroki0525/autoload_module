"""Module contains custom exceptions for the autoload module."""


class LoaderStrictModeError(Exception):
    """If ModuleLoader is initialized by strict mode, This will be raised."""
