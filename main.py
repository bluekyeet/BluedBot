import discord
import os
import aiohttp
import threading
from ServerExpiryChecker import checker
from LinkvertiseWebserver import webserver
from discord.ext import commands
from dotenv import load_dotenv
from database.DatabaseEngine import engine
from database.DatabaseModels import metadata

load_dotenv()

def initdb():
    metadata.create_all(engine)

class BluedHostBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix='bh#',
            intents=discord.Intents.all(),
            application_id=int(os.getenv("DISCORD_BOT_APPLICATION_ID")),
            help_command=None
        )
        self.session = None
        self.initial_extensions = ["cogs.Coins"]

        if str(os.getenv("LINKVERTISE_SYSTEM")).lower() == "enable":
            self.initial_extensions.append("cogs.Linkvertise")
        if str(os.getenv("SERVER_EXPIRY_SYSTEM")).lower() == "enable":
            self.initial_extensions.append("cogs.RenewServer")


    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

        for ext in self.initial_extensions:
            await self.load_extension(ext)

        await self.tree.sync(guild=discord.Object(id=1367424444850634863))

    async def close(self):
        await super().close()
        if self.session:
            await self.session.close()

    async def on_ready(self):
        initdb()
        print(f'Logged in as {self.user} (ID: {self.user.id})')


if str(os.getenv("LINKVERTISE_SYSTEM")).lower() == 'enable':
    webserver_thread = threading.Thread(target=webserver)
    webserver_thread.daemon = True
    webserver_thread.start()

if str(os.getenv("SERVER_EXPIRY_SYSTEM")).lower() == "enable":
    expire_check_thread = threading.Thread(target=checker)
    expire_check_thread.daemon = True
    expire_check_thread.start()

bot = BluedHostBot()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))
