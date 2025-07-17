from sqlalchemy import Table, Column, Integer, String, MetaData

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("discord_id", Integer, primary_key=True),
    Column("user_uid", Integer, nullable=False),
    Column("coins", Integer, default=0),
    Column("claimed_boost_reward", Integer, default=0),
    Column("lvcount", Integer, default=0),
    Column("lvcount_date", String, nullable=True),
    Column("avaliable_server_slots", Integer, default=1),
    Column("used_server_slots", Integer, default=0),
)

servers = Table(
    "servers",
    metadata,
    Column("server_id", Integer, primary_key=True),
    Column("user_uid", Integer),
    Column("server_level", Integer, default=0),
    Column("server_last_renew_date", Integer)
)
