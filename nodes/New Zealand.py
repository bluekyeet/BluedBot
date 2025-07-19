def node():
    node_info = {
        "name": "New Zealand",
        "node_id": 1
    }
    eggs_blacklist = ["Paper", "Fabric"]
    node_server_limit = {
        "cpu": 50,
        "ram": 512,
        "disk": 1024
    }

    return node_info, eggs_blacklist, node_server_limit