import datetime
import os

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from database.DatabaseConfig import DB_BACKEND, MYSQL_CONFIG, SQLITE_PATH

if DB_BACKEND == "mysql":
    engine = create_engine(
        f"mysql+mysqlconnector://{MYSQL_CONFIG['user']}:{MYSQL_CONFIG['password']}@"
        f"{MYSQL_CONFIG['host']}/{MYSQL_CONFIG['database']}",
        echo=False, future=True
    )
else:
    engine = create_engine(f"sqlite:///{SQLITE_PATH}", echo=False, future=True)

def get_connection():
    return engine.connect()

def check_user_exists(discord_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT 1 FROM users WHERE discord_id = :discord_id"), {"discord_id": discord_id}).fetchone()
    except SQLAlchemyError:
        return 400
    return bool(result)

def create_user(discord_id, user_uid):
    try:
        with get_connection() as conn:
            conn.execute(text("INSERT INTO users (discord_id, user_uid) VALUES (:discord_id, :user_uid)"), {"discord_id": discord_id, "user_uid": user_uid})
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def get_user_uid(discord_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT user_uid FROM users WHERE discord_id = :discord_id"), {"discord_id": discord_id}).fetchone()
    except SQLAlchemyError:
        return 400
    return result[0] if result else False

def get_user_info(discord_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT * FROM users WHERE discord_id = :discord_id"), {"discord_id": discord_id}).fetchone()
    except SQLAlchemyError:
        return 400
    return result if result else False

def check_coin_count(discord_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT coins FROM users WHERE discord_id = :discord_id"), {"discord_id": discord_id}).fetchone()
    except SQLAlchemyError:
        return 400
    return result[0] if result else 0

def update_coin_count(discord_id, amount):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET coins = coins + :amount WHERE discord_id = :discord_id"), {"amount": amount, "discord_id": discord_id})
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def boost_rewards_claimed(discord_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT claimed_boost_reward FROM users WHERE discord_id = :discord_id"), {"discord_id": discord_id}).fetchone()
    except SQLAlchemyError:
        return 400
    return result[0] if result else False

def update_boost_rewards_claimed(discord_id, param):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET claimed_boost_reward = :param WHERE discord_id = :discord_id"), {"param": param, "discord_id": discord_id})
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def get_linkvertise_info(discord_id):
    try:
        with get_connection() as conn:
            return conn.execute(text("SELECT lvcount, lvcount_date FROM users WHERE discord_id = :discord_id"), {"discord_id": discord_id}).fetchone()
    except SQLAlchemyError:
        return 400

def update_linkvertise_count(discord_id, param):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET lvcount = :param WHERE discord_id = :discord_id"), {"param": param, "discord_id": discord_id})
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def update_linkvertise_date(discord_id, param):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET lvcount_date = :param WHERE discord_id = :discord_id"), {"param": param, "discord_id": discord_id})
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def get_all_server_expiry_times():
    try:
        with get_connection() as conn:
            return conn.execute(text("SELECT server_id, server_last_renew_date FROM servers")).fetchall()
    except SQLAlchemyError:
        return 400

def add_server(server_id, user_id, cpu, ram, disk):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET used_server_slots = used_server_slots + 1 WHERE user_uid = :user_id"), {"user_id": user_id})
            conn.execute(text("UPDATE users SET used_cpu = used_cpu + :cpu WHERE user_uid = :user_id"),{"user_id": user_id, "cpu": cpu})
            conn.execute(text("UPDATE users SET used_ram = used_ram + :ram WHERE user_uid = :user_id"),{"user_id": user_id, "ram": ram})
            conn.execute(text("UPDATE users SET used_disk = used_disk + :disk WHERE user_uid = :user_id"),{"user_id": user_id, "disk": disk})
            conn.execute(text("INSERT INTO servers (server_id, user_uid, server_level, server_last_renew_date, cpu, ram, disk) VALUES (:server_id, :user_id, 0, :renew_date, :cpu, :ram, :disk)"), {
                "server_id": server_id,
                "user_id": user_id,
                "renew_date": int(datetime.datetime.now(datetime.timezone.utc).timestamp()),
                "cpu": cpu,
                "ram": ram,
                "disk": disk
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def check_if_user_owns_that_server(discord_id, server_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT user_uid FROM servers WHERE server_id = :server_id"), {"server_id": server_id}).fetchone()
        if not result or get_user_uid(discord_id) != result[0]:
            return False
    except SQLAlchemyError:
        return 400
    return True

def check_if_server_exists(server_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT server_id FROM servers WHERE server_id = :server_id"), {"server_id": server_id}).fetchone()
    except SQLAlchemyError:
        return 400
    return bool(result)

def renew_server(server_id):
    try:
        with get_connection() as conn:
            last_renew = get_single_server_info(server_id)[1]
            now = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            renew_time = now if last_renew <= now - (int(os.getenv("SERVER_RENEW_DAYS"))*86400) else last_renew + (int(os.getenv("SERVER_RENEW_DAYS"))*86400)
            conn.execute(text("UPDATE servers SET server_last_renew_date = :renew_time WHERE server_id = :server_id"), {
                "renew_time": renew_time,
                "server_id": server_id
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def suspend_server(server_id):
    try:
        with get_connection() as conn:
            renew_time = 0
            conn.execute(text("UPDATE servers SET server_last_renew_date = :renew_time WHERE server_id = :server_id"), {
                "renew_time": renew_time,
                "server_id": server_id
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def get_all_servers_info(discord_id):
    try:
        with get_connection() as conn:
            return conn.execute(text("SELECT server_id, server_level, server_last_renew_date, cpu, ram, disk FROM servers WHERE user_uid = :user_uid"), {
                "user_uid": get_user_uid(discord_id)
            }).fetchall()
    except SQLAlchemyError:
        return 400

def get_single_server_info(server_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT server_level, server_last_renew_date, cpu, ram, disk FROM servers WHERE server_id = :server_id"), {"server_id": server_id}).fetchone()
    except SQLAlchemyError:
        return 400
    return result if result else False

def delete_server(server_id, user_id):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET used_server_slots = used_server_slots - 1 WHERE user_uid = :user_uid"), {"user_uid": get_user_uid(user_id)})
            conn.execute(text("DELETE FROM servers WHERE server_id = :server_id"), {"server_id": server_id})
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def upgrade_server(server_id, level):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE servers SET server_level = :level WHERE server_id = :server_id"), {
                "level": level,
                "server_id": server_id
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def edit_server(server_id, cpu, ram, disk):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE servers SET cpu = :cpu WHERE server_id = :server_id"), {"cpu": cpu, "server_id": server_id})
            conn.execute(text("UPDATE servers SET ram = :ram WHERE server_id = :server_id"),{"ram": ram, "server_id": server_id})
            conn.execute(text("UPDATE servers SET disk = :disk WHERE server_id = :server_id"),{"disk": disk, "server_id": server_id})
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def check_if_user_has_any_servers(discord_id):
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT server_id FROM servers WHERE user_uid = :user_uid"), {
                "user_uid": get_user_uid(discord_id)
            }).fetchone()
    except SQLAlchemyError:
        return 400
    return bool(result)

def update_server_slots(discord_id, param):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET available_server_slots = available_server_slots + :param WHERE discord_id = :discord_id"), {
                "param": param,
                "discord_id": discord_id
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def add_invite(inviter, user):
    try:
        with get_connection() as conn:
            conn.execute(text("INSERT INTO invite(inviter, user) VALUES(:inviter, :user)"), {
                "inviter": inviter,
                "user": user
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def check_if_invite_exists(inviter, user):
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT * FROM invite WHERE inviter = :inviter AND userid = :user"), {
                "inviter": inviter,
                "user": user
            }).fetchone()
        if not result or not result[0]:
            return False
    except SQLAlchemyError:
        return 400
    return True

def update_blacklist_status(discord_id, param):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET blacklist_status = :param WHERE discord_id = :discord_id"), {
                "param": param,
                "discord_id": discord_id
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def get_blacklist_status(discord_id):
    try:
        with get_connection() as conn:
            result = conn.execute(
                text("SELECT blacklist_status FROM users WHERE discord_id = :discord_id"),
                {"discord_id": discord_id}
            ).fetchone()

            if result is None or result[0] is None:
                return 0
            return result[0]
    except SQLAlchemyError as e:
        return 400

def update_cpu(discord_id, param):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET available_cpu = available_cpu + :param WHERE discord_id = :discord_id"), {
                "param": param,
                "discord_id": discord_id
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def update_ram(discord_id, param):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET available_ram = available_ram + :param WHERE discord_id = :discord_id"), {
                "param": param,
                "discord_id": discord_id
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def update_disk(discord_id, param):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET available_disk = available_disk + :param WHERE discord_id = :discord_id"), {
                "param": param,
                "discord_id": discord_id
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def update_used_resources(user_id, cpu, ram, disk):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE users SET used_cpu = used_cpu + :cpu WHERE user_uid = :user_id"), {"user_id": user_id, "cpu": cpu})
            conn.execute(text("UPDATE users SET used_ram = used_ram + :ram WHERE user_uid = :user_id"),{"user_id": user_id, "ram": ram})
            conn.execute(text("UPDATE users SET used_disk = used_disk + :disk WHERE user_uid = :user_id"),{"user_id": user_id, "disk": disk})
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200

def get_config():
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT * FROM config")).fetchone()
    except SQLAlchemyError:
        return 400
    return result if result else False

def update_renew_system(param):
    try:
        with get_connection() as conn:
            conn.execute(text("UPDATE config SET renew_system = :param"), {
                "param": param
            })
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200


def update_all_servers_expire():
    try:
        with get_connection() as conn:
            renew_date = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            conn.execute(
                text("UPDATE servers SET server_last_renew_date = :renew_date"),
                {"renew_date": renew_date}
            )
            conn.commit()
    except SQLAlchemyError:
        return 400
    return 200


def initialize_config_table():
    try:
        with get_connection() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM config")).scalar()
            if result == 0:
                conn.execute(text("INSERT INTO config (renew_system) VALUES (2)"))
                conn.commit()
    except SQLAlchemyError as e:
        return 0


    