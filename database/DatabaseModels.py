from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("discord_id", Integer, primary_key=True),
    Column("user_uid", Integer, nullable=False),
    Column("coins", Integer, default=0, server_default="0"),
    Column("claimed_boost_reward", Integer, default=0, server_default="0"),
    Column("lvcount", Integer, default=0, server_default="0"),
    Column("lvcount_date", String, nullable=True),
    Column("available_server_slots", Integer, default=0, server_default="0"),
    Column("used_server_slots", Integer, default=0, server_default="0"),
    Column("blacklist_status", Integer, default=0, server_default="0"),
    Column("available_cpu", Integer, default=0, server_default="0"),
    Column("available_ram", Integer, default=0, server_default="0"),
    Column("available_disk", Integer, default=0, server_default="0"),
    Column("used_cpu", Integer, default=0, server_default="0"),
    Column("used_ram", Integer, default=0, server_default="0"),
    Column("used_disk", Integer, default=0, server_default="0"),
)

servers = Table(
    "servers",
    metadata,
    Column("server_id", Integer, primary_key=True),
    Column("user_uid", Integer),
    Column("server_level", Integer, default=0, server_default="0"),
    Column("server_last_renew_date", Integer),
    Column("cpu", Integer, default=0, server_default="0"),
    Column("ram", Integer, default=0, server_default="0"),
    Column("disk", Integer, default=0, server_default="0")
)

invite = Table(
    "invite",
    metadata,
    Column("inviter", Integer),
    Column("userid", Integer),
)

config = Table(
    "config",
    metadata,
    Column("renew_system", Integer, nullable=True, default=2)
)