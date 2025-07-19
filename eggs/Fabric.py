def egg(name: str, userid: int, memory: int, disk: int, cpu: int, port: int):
    config = {
      "name": name,
      "user": userid,
      "egg": 4,
      "docker_image": "ghcr.io/parkervcp/yolks:java_21",
      "startup": "java -Xms128M -Xmx{{SERVER_MEMORY}}M -jar {{SERVER_JARFILE}}",
      "environment": {
        "MC_VERSION": "latest",
        "FABRIC_VERSION": "latest",
        "LOADER_VERSION": "latest",
        "SERVER_JARFILE": "server.jar"
      },
      "limits": {
        "memory": memory,
        "swap": -1,
        "disk": disk,
        "io": 500,
        "cpu": cpu
      },
      "feature_limits": {
        "databases": 0,
        "backups": 0
      },
      "allocation": {
        "default": port
      }
    }
    limits = {
      "memory_max": 8192,
      "disk_max": 8192,
      "cpu_max": 400,
    }
    return config, limits