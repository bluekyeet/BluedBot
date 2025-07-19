import discord
import os
import EmbedHandler
import Logger
from database import DatabaseHandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    moderation_command = app_commands.Group(name="moderation", description="Moderation commands")

    @moderation_command.command(name="blacklist", description="The account you want to blacklist from the host.")
    async def blacklist(self, interaction: discord.Interaction, user: discord.User):
        if DatabaseHandler.get_blacklist_status(interaction.user.id) != 0:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
            )
            return
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

    @moderation_command.command(name="unblacklist", description="The account you want to unblacklist from the host.")
    async def unblacklist(self, interaction: discord.Interaction, user: discord.User):
        if DatabaseHandler.get_blacklist_status(interaction.user.id) != 0:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
            )
            return
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

    @moderation_command.command(name="addcoins", description="Add an amount of coins to a specific user.")
    @app_commands.describe(user="The Discord user of the person you want to add coins to.",
                           amount="The amount of coins you want to add to an user.")
    async def addcoins(self, interaction: discord.Interaction, user: discord.User, amount: int):
        if DatabaseHandler.get_blacklist_status(interaction.user.id) != 0:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
            )
            return
        if interaction.user.get_role(int(os.getenv("DISCORD_SERVER_ADMIN_ROLE_ID"))) is None:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
            )
        else:
            try:
                if not DatabaseHandler.check_user_exists(user.id) or DatabaseHandler == 400:
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="The user you are trying to add coins to doesn't have an account."
                        ),
                        ephemeral=True
                    )
                    return

                DatabaseHandler.update_coin_count(user.id, amount)

                await interaction.response.send_message(
                    embed=EmbedHandler.success(
                        message=f"Added {amount} coins to <@{user.id}> successfully. They have {DatabaseHandler.check_coin_count(user.id)} coins now."
                    )
                )

                Logger.send_webhook(f"{interaction.user.name} added {amount} coins to <@{user.id}>.")

            except Exception as e:
                print(e)
                await interaction.response.send_message(
                    embed=EmbedHandler.error(
                        message="Something went wrong. Please contact support."
                    ),
                    ephemeral=True
                )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Moderation(bot), guilds=[discord.Object(id=os.getenv("DISCORD_SERVER_ID"))])
