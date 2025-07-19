import datetime
import os
import discord
import EmbedHandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from database import DatabaseHandler

load_dotenv()

class Linkvertise(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="linkvertise", description="Go to the Linkvertise link generation page to earn coins.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    async def linkvertise(self, interaction: discord.Interaction):
        if DatabaseHandler.get_blacklist_status(interaction.user.id) != 0:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
            )
            return
        if os.getenv("LINKVERTISE_SYSTEM").lower() != "enable":
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="Linkvertise is disabled."
                ),
                ephemeral=True
            )
            return
        if interaction.channel.id != int(os.getenv("DISCORD_SERVER_COMMAND_CHANNEL_ID")):
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="Wrong channel!"
                ),
                ephemeral=True
            )
        try:
            if not DatabaseHandler.check_user_exists(interaction.user.id) or DatabaseHandler == 400:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You don't have an account."
                    ),
                    ephemeral=True
                )
                return
            linkvertise_data = DatabaseHandler.get_linkvertise_info(interaction.user.id)

            if linkvertise_data == 400:
                await interaction.response.send_message(
                    embed=EmbedHandler.error(
                        "Something went wrong. Please contact support."
                    ),
                    ephemeral=True
                )
                return

            linkvertise_count = (int(linkvertise_data[0] or 0))
            linkvertise_date = linkvertise_data[1]

            if linkvertise_count >= int(os.getenv("LINKVERTISE")):
                if datetime.date.fromisoformat(linkvertise_date) < datetime.date.today() or linkvertise_date is None:
                    DatabaseHandler.update_linkvertise_count(interaction.user.id, 0)
                else:
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You have reached the maximum amount of Linkvertise attempts today."
                        ),
                        ephemeral=True
                    )
                    return

            await interaction.response.send_message(
                embed=EmbedHandler.information(
                    message=f'Your Linkvertise link generation page is [here]({os.getenv("LINKVERTISE_LINK")}/generate?user_id={interaction.user.id}).'
                ),
                ephemeral=True
            )

        except Exception as e:
            print(e)
            await interaction.response.send_message(
                embed=EmbedHandler.error(
                    message="Something went wrong. Please contact support."
                ),
                ephemeral=True
            )

    @linkvertise.error
    async def error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Linkvertise(bot), guilds=[discord.Object(id=os.getenv("DISCORD_SERVER_ID"))])