"""Provides the autoload functionality.

Including the ModuleLoader, ModuleLoaderSetting, and the load_config decorator.
"""

from .decorator import load_config
from .module_loader import ModuleLoader, ModuleLoaderSetting

__all__ = (
    "ModuleLoader",
    "ModuleLoaderSetting",
    "load_config",
)
