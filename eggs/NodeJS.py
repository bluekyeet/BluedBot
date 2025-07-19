def egg(name: str, userid: int, memory: int, disk: int, cpu: int, port: int):
    config = {
      "name": name,
      "user": userid,
      "egg": 15,
      "docker_image": 'ghcr.io/pelican-eggs/yolks:nodejs_24',
      "startup": 'if [[ -d .git ]] && [[ {{AUTO_UPDATE}} == "1" ]]; then git pull; fi; if [[ ! -z ${NODE_PACKAGES} ]]; then /usr/local/bin/npm install ${NODE_PACKAGES}; fi; if [[ ! -z ${UNNODE_PACKAGES} ]]; then /usr/local/bin/npm uninstall ${UNNODE_PACKAGES}; fi; if [ -f /home/container/package.json ]; then /usr/local/bin/npm install; fi; if [[ "${MAIN_FILE}" == "*.js" ]]; then /usr/local/bin/node "/home/container/${MAIN_FILE}" ${NODE_ARGS}; else /usr/local/bin/ts-node --esm "/home/container/${MAIN_FILE}" ${NODE_ARGS}; fi',
      "environment": {
        "AUTO_UPDATE": 0,
        "MAIN_FILE": "index.js",
        "USER_UPLOAD": 0
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