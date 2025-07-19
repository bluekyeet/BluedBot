# nodes/__init__.py
# noinspection PyUnresolvedReferences
# noinspection PyUnresolvedReferences,PyPackageRequirements

import os
import importlib
import sys

__all__ = []

folder = os.path.dirname(__file__)
package = __name__

for filename in os.listdir(folder):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = filename[:-3]
        full_module_name = f"{package}.{module_name}"
        module = importlib.import_module(full_module_name)

        setattr(sys.modules[package], module_name, module)

        __all__.append(module_name)