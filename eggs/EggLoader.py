import importlib
import os

EGG_MODULES = {}
EGG_IDS = {}

def load_eggs():
    egg_dir = os.path.dirname(__file__)
    for filename in os.listdir(egg_dir):
        if filename.endswith(".py") and filename != "EggLoader.py" and not filename.startswith("__"):
            module_name = filename[:-3]
            module_path = f"eggs.{module_name}"
            try:
                mod = importlib.import_module(module_path)
                if hasattr(mod, "egg") and callable(mod.egg):
                    EGG_MODULES[module_name] = mod.egg
                    config, _ = mod.egg("placeholder", 0, 512, 1024, 100, 25565)
                    egg_id = config.get("egg")
                    if egg_id is not None:
                        EGG_IDS[egg_id] = module_name
                else:
                    print(f"[Warning] '{module_name}' does not have a callable 'egg' attribute.")
            except Exception as e:
                print(f"[Error] Failed to load {module_name}: {e}")

def get_egg_by_name(name: str):
    return EGG_MODULES.get(name)

def get_egg_by_id(egg_id: int):
    module_name = EGG_IDS.get(egg_id)
    if module_name:
        return EGG_MODULES.get(module_name)
    return None, None