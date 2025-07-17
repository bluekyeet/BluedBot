import sqlite3
import datetime

def get_connection():
    return sqlite3.connect('database.db')

def check_user_exists(discord_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
            user = c.fetchone()
    except sqlite3.OperationalError:
        return 400
    if user is None:
        return False
    return True

def create_user(discord_id, user_uid):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("INSERT INTO users (discord_id, user_uid) VALUES (?, ?)", (discord_id, user_uid))
            conn.commit()
    except sqlite3.IntegrityError:
        return 400
    return 200

def get_user_uid(discord_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT user_uid FROM users WHERE discord_id = ?", (discord_id,))
            user_uid = c.fetchone()
    except sqlite3.OperationalError:
        return 400
    if user_uid is None or user_uid[0] is None:
        return False
    return user_uid[0]

def get_user_info(discord_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE discord_id = ?", (discord_id,))
            user_info = c.fetchone()
    except sqlite3.OperationalError:
        return 400
    if user_info is None or user_info[0] is None:
        return False
    return user_info

def check_coin_count(discord_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT coins FROM users WHERE discord_id = ?", (discord_id,))
            coins = c.fetchone()
    except sqlite3.OperationalError:
        return 400
    if coins is None or coins[0] is None:
        return 0
    return coins[0]

def update_coin_count(discord_id, amount):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET coins = coins + ? WHERE discord_id = ?", (amount, discord_id))
            conn.commit()
    except sqlite3.OperationalError:
        return 400
    return 200

def boost_rewards_claimed(discord_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT claimed_boost_reward FROM users WHERE discord_id = ?", (discord_id,))
            user_info = c.fetchone()
    except sqlite3.OperationalError:
        return 400
    if user_info is None or user_info[0] is None:
        return False
    return user_info[0]

def update_boost_rewards_claimed(discord_id, param):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET claimed_boost_reward = ? WHERE discord_id = ?", (param, discord_id))
            conn.commit()
    except sqlite3.OperationalError:
        return 400
    return 200

def get_linkvertise_info(discord_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT lvcount, lvcount_date FROM users WHERE discord_id = ?", (discord_id,))
            linkvertise_info = c.fetchone()
    except sqlite3.OperationalError:
        return 400
    return linkvertise_info

def update_linkvertise_count(discord_id, param):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET lvcount = ? WHERE discord_id = ?", (param, discord_id))
            conn.commit()
    except sqlite3.OperationalError:
        return 400
    return 200

def update_linkvertise_date(discord_id, param):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET lvcount_date = ? WHERE discord_id = ?", (param, discord_id))
            conn.commit()
    except sqlite3.OperationalError:
        return 400
    return 200

def check_if_user_has_slots(discord_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT avaliable_server_slots, used_server_slots FROM users WHERE discord_id = ?", (discord_id,))
            server_slots = c.fetchone()
    except sqlite3.OperationalError:
        return 400
    if server_slots is None or server_slots[0] is None:
        return False
    if server_slots[0] <= server_slots[1]:
        return False
    return True

def get_all_server_expiry_times():
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT server_id, server_last_renew_date FROM servers")
            servers = c.fetchall()
    except sqlite3.OperationalError:
        return 400
    return servers

def add_server(server_id, user_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET used_server_slots = used_server_slots + 1 WHERE user_uid = ?", (user_id,))
            c.execute("INSERT INTO servers (server_id, user_uid, server_level, server_last_renew_date) VALUES (?, ?, ?, ?)", (server_id, user_id, 0, int((datetime.datetime.now(datetime.UTC).timestamp())//1)))
            conn.commit()
    except sqlite3.OperationalError:
        return 400
    return 200

def check_if_user_owns_that_server(discord_id, server_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT user_uid FROM servers WHERE server_id = ?", (server_id,))
            server_info = c.fetchone()
        if server_info is None or server_info[0] is None:
            return False
        if get_user_uid(discord_id) != server_info[0]:
            return False
    except sqlite3.OperationalError:
        return 400
    return True

def check_if_server_exists(server_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT server_id FROM servers WHERE server_id = ?", (server_id,))
            server_info = c.fetchone()
    except sqlite3.OperationalError:
        return 400
    if server_info is None or server_info[0] is None:
        return False
    return True

def renew_server(server_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            last_renew = get_single_server_info(server_id)[1]
            if last_renew <= int((datetime.datetime.now(datetime.UTC).timestamp() - 604800) // 1):
                renew_time = int((datetime.datetime.now(datetime.UTC).timestamp()) // 1)
            else:
                renew_time = last_renew + 604800
            c.execute("UPDATE servers SET server_last_renew_date = ? WHERE server_id = ?", (renew_time, server_id))
    except sqlite3.OperationalError:
        return 400
    return 200

def get_all_servers_info(discord_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT server_id, server_level, server_last_renew_date FROM servers WHERE user_uid = ?", (get_user_uid(discord_id),))
            server_info = c.fetchall()
    except sqlite3.OperationalError:
        return 400
    if not server_info:
        return False
    return server_info

def get_single_server_info(server_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT server_level, server_last_renew_date FROM servers WHERE server_id = ?", (server_id,))
            server_info = c.fetchone()
    except sqlite3.OperationalError:
        return 400
    if not server_info:
        return False
    return server_info

def delete_server(server_id, user_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET used_server_slots = used_server_slots - 1 WHERE user_uid = ?", (get_user_uid(user_id),))
            c.execute("DELETE FROM servers WHERE server_id = ?", (server_id,))
            conn.commit()
    except sqlite3.OperationalError:
        return 400
    return 200

def upgrade_server(server_id, level):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE servers SET server_level = ? WHERE server_id = ?", (level, server_id))
            conn.commit()
    except sqlite3.OperationalError:
        return 400
    return 200


def check_if_user_has_any_servers(discord_id):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT server_id FROM servers WHERE user_uid = ?", (get_user_uid(discord_id),))
            server_info = c.fetchone()
    except sqlite3.OperationalError:
        return 400
    if server_info is None or server_info[0] is None:
        return False
    return True


def update_server_slots(discord_id, param):
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET avaliable_server_slots = avaliable_server_slots + ? WHERE discord_id = ?", (param, discord_id))
            conn.commit()
    except sqlite3.OperationalError:
        return 400
    return 200