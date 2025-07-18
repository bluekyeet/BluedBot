import discord
import os
import EmbedHandler
from database import DatabaseHandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="blacklist", description="The account you want to blacklist from the host.")
    async def blacklist(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user.get_role(int(os.getenv("DISCORD_SERVER_ADMIN_ROLE_ID"))) is None and interaction.user.get_role(int(os.getenv("DISCORD_SERVER_MODERATOR_ROLE_ID"))) is None:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
            )
            return
        await interaction.response.send_message(
            embed=EmbedHandler.information(
                message=f"Successfully blacklisted {user.mention}.",
            ),
        )
        DatabaseHandler.update_blacklist_status(user.id, 1)

    @app_commands.command(name="unblacklist", description="The account you want to unblacklist from the host.")
    async def unblacklist(self, interaction: discord.Interaction, user: discord.User):
        if interaction.user.get_role(int(os.getenv("DISCORD_SERVER_ADMIN_ROLE_ID"))) is None and interaction.user.get_role(int(os.getenv("DISCORD_SERVER_MODERATOR_ROLE_ID"))) is None:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
            )
            return
        await interaction.response.send_message(
            embed=EmbedHandler.information(
                message=f"Successfully unblacklisted {user.mention}.",
            ),
        )
        DatabaseHandler.update_blacklist_status(user.id, 0)



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot), guilds=[discord.Object(id=os.getenv("DISCORD_SERVER_ID"))])
