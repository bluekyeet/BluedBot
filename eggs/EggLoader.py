import importlib
import os

EGG_MODULES = {}

def load_eggs():
    egg_dir = os.path.dirname(__file__)
    for filename in os.listdir(egg_dir):
        if filename.endswith(".py") and filename != "EggLoader.py" and not filename.startswith("__"):
            module_name = filename[:-3]
            module_path = f"eggs.{module_name}"
            mod = importlib.import_module(module_path)
            if hasattr(mod, "egg"):
                EGG_MODULES[module_name] = mod.egg

def get_egg_by_name(name: str):
    return EGG_MODULES.get(name)
