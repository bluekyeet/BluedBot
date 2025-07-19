import importlib
import os

NODES = {}
NODE_IDS = {}

def load_nodes():
    node_dir = os.path.dirname(__file__)
    for filename in os.listdir(node_dir):
        if filename.endswith(".py") and filename != "NodesLoader.py" and not filename.startswith("__"):
            module_name = filename[:-3]
            module_path = f"nodes.{module_name}"
            try:
                mod = importlib.import_module(module_path)
                if hasattr(mod, "node") and callable(mod.node):
                    node = mod.node()
                    if isinstance(node, tuple) and len(node) == 3:
                        NODES[module_name] = node
                        node_info = node[0]
                        node_id = node_info.get("node_id")
                        if node_id is not None:
                            NODE_IDS[node_id] = module_name
                    else:
                        print(f"[Warning] '{module_name}' has an invalid 'node' attribute. Expected a tuple with 3 elements.")
                else:
                    print(f"[Warning] '{module_name}' does not have a callable 'node' attribute.")
            except Exception as e:
                print(f"[Error] Failed to load {module_name}: {e}")

def get_node_by_name(name: str):
    return NODES.get(name)

def get_node_by_node_id(node_id: int):
    module_name = NODE_IDS.get(node_id)
    if module_name:
        return NODES.get(module_name)
    return None, None, None