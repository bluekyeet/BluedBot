import importlib
import os

NODES = {}

def load_nodes():
    node_dir = os.path.dirname(__file__)
    for filename in os.listdir(node_dir):
        if filename.endswith(".py") and filename != "NodesLoader.py" and not filename.startswith("__"):
            module_name = filename[:-3]
            module_path = f"nodes.{module_name}"
            try:
                mod = importlib.import_module(module_path)
                if hasattr(mod, "node"):
                    NODES[module_name] = mod.node
                else:
                    print(f"[Warning] '{module_name}' does not have a 'node' attribute.")
            except Exception as e:
                print(f"[Error] Failed to load {module_name}: {e}")

def get_node_by_name(name: str):
    return NODES.get(name)
