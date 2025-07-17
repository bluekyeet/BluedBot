from sqlalchemy import create_engine
from DatabaseConfig import DB_BACKEND, MYSQL_CONFIG, SQLITE_PATH

if DB_BACKEND == "mysql":
    url = f"mysql+pymysql://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@{MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}"
else:
    url = f"sqlite:///{SQLITE_PATH}"

engine = create_engine(url, echo=False, future=True)
