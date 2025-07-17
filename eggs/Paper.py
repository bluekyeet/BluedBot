def egg(name: str, userid: int, memory: int, disk: int, cpu: int, port: int):
    config = {
      "name": name,
      "user": userid,
      "egg": 1,
      "docker_image": "ghcr.io/parkervcp/yolks:java_21",
      "startup": "java -Xms128M -XX:MaxRAMPercentage=95.0 -Dterminal.jline=false -Dterminal.ansi=true -jar {{SERVER_JARFILE}}",
      "environment": {
        "BUILD_NUMBER": "latest",
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