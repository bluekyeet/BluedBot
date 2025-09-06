import discord
import os
import aiohttp
import threading
from ServerExpiryChecker import checker, load_system
from LinkvertiseWebserver import webserver
from discord.ext import commands
from dotenv import load_dotenv
from database.DatabaseEngine import engine
from database.DatabaseModels import metadata
from database import DatabaseHandler
from datetime import datetime, timezone, timedelta
from eggs.EggLoader import load_eggs
from nodes.NodesLoader import load_nodes

load_dotenv()

def initdb():
    metadata.create_all(engine)

invite_cache = {}

class BluedHostBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix='bh#',
            intents=discord.Intents.all(),
            application_id=int(os.getenv("DISCORD_BOT_APPLICATION_ID")),
            help_command=None
        )
        self.session = None
        self.initial_extensions = ["cogs.Coins", "cogs.Account", "cogs.Help", "cogs.Admin", "cogs.Server"]

        if str(os.getenv("LINKVERTISE_SYSTEM")).lower() == "enable":
            self.initial_extensions.append("cogs.Linkvertise")


    async def setup_hook(self):
        self.session = aiohttp.ClientSession()

        initdb()
        load_eggs()
        load_nodes()

        DatabaseHandler.initialize_config_table()

        load_system()

        for ext in self.initial_extensions:
            await self.load_extension(ext)

        await self.tree.sync(guild=discord.Object(id=os.getenv("DISCORD_SERVER_ID")))

    async def close(self):
        await super().close()
        if self.session:
            await self.session.close()

    async def on_ready(self):
        if os.getenv("INVITE_REWARDS").lower() == "enable":
            guild = bot.guilds[0]
            invites = await guild.invites()
            invite_cache[guild.id] = {invite.code: invite.uses for invite in invites}
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_member_join(self, member):
        if os.getenv("INVITE_REWARDS").lower() == "enable":
            guild = member.guild
            new_invites = await guild.invites()
            old_invites = invite_cache.get(guild.id, {})
            used_invite = None

            for invite in new_invites:
                if invite.code in old_invites and invite.uses > old_invites[invite.code]:
                    used_invite = invite
                    break

            invite_cache[guild.id] = {i.code: i.uses for i in new_invites}

            if used_invite:
                now = datetime.now(timezone.utc)
                account_age = now - member.created_at
                inviter = used_invite.inviter
                if DatabaseHandler.get_blacklist_status(inviter.id) != 0:
                    return
                if not DatabaseHandler.check_user_exists(inviter.id):
                    await guild.get_channel(int(os.getenv("DISCORD_SERVER_WELCOME_INVITE_CHANNEL_ID"))).send(f"Hello {member.mention}, welcome to the server! You were invited by {inviter.name}.")
                    return
                if not DatabaseHandler.check_if_invite_exists(inviter.id, member.id):
                    DatabaseHandler.add_invite(inviter.id, member.id)
                    if account_age < timedelta(days=7):
                        await guild.get_channel(int(os.getenv("DISCORD_SERVER_WELCOME_INVITE_CHANNEL_ID"))).send(
                            f"Hello {member.mention}, welcome to the server! You were invited by {inviter.name}. Account age is less than 7 days.")
                        return
                    await guild.get_channel(int(os.getenv("DISCORD_SERVER_WELCOME_INVITE_CHANNEL_ID"))).send(f"Hello {member.mention}, welcome to the server!, you were invited by {inviter.name}. {inviter.mention} has been rewarded with {os.getenv('INVITE_REWARD')} coins for inviting you!")
                    DatabaseHandler.update_coin_count(inviter.id, os.getenv('INVITE_REWARD'))
                    return
                else:
                    await guild.get_channel(int(os.getenv("DISCORD_SERVER_WELCOME_INVITE_CHANNEL_ID"))).send(f"Hello {member.mention}, welcome to the server! You were invited by {inviter.name}.")
                    return
            else:
                await guild.get_channel(int(os.getenv("DISCORD_SERVER_WELCOME_INVITE_CHANNEL_ID"))).send(f"Hello {member.mention}, welcome to the server!")
                return
        else:
            guild = member.guild
            await guild.get_channel(int(os.getenv("DISCORD_SERVER_WELCOME_INVITE_CHANNEL_ID"))).send(f"Hello {member.mention}, welcome to the server!")
            return

    async def on_invite_create(self, invite):
        if os.getenv("INVITE_REWARDS").lower() == "enable":
            invites = await invite.guild.invites()
            invite_cache[invite.guild.id] = {i.code: i.uses for i in invites}

    async def on_invite_delete(self, invite):
        if os.getenv("INVITE_REWARDS").lower() == "enable":
            invites = await invite.guild.invites()
            invite_cache[invite.guild.id] = {i.code: i.uses for i in invites}



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
