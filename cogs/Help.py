import discord
import os
import EmbedHandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="help", description="Help command.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def help(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            embed=EmbedHandler.help_embed()
        )

    @help.error
    async def help_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot), guilds=[discord.Object(id=int(os.getenv("DISCORD_SERVER_ID")))])
