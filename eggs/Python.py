def egg(name: str, userid: int, memory: int, disk: int, cpu: int, port: int):
    config = {
      "name": name,
      "user": userid,
      "egg": 16,
      "docker_image": "ghcr.io/parkervcp/yolks:python_3.13",
      "startup": 'if [[ -d .git ]] && [[ "{{AUTO_UPDATE}}" == "1" ]]; then git pull; fi; if [[ ! -z "{{PY_PACKAGES}}" ]]; then pip install -U --prefix .local {{PY_PACKAGES}}; fi; if [[ -f /home/container/${REQUIREMENTS_FILE} ]]; then pip install -U --prefix .local -r ${REQUIREMENTS_FILE}; fi; /usr/local/bin/python /home/container/{{PY_FILE}}',
      "environment": {
        "AUTO_UPDATE": 0,
        "PY_FILE": "app.py",
        "REQUIREMENTS_FILE": "requirements.txt"
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
      "memory_max": 512,
      "disk_max": 1024,
      "cpu_max": 50,
    }
    return config, limits