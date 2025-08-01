import random
import string
import discord
import requests
import os
import re
import EmbedHandler
import Logger
from database import DatabaseHandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

class Account(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    account_command = app_commands.Group(name="account", description="Account management commands")

    @account_command.command(name="create", description="Create an account on the panel")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(email="The email of the account you want to create.")
    async def create(self, interaction: discord.Interaction, email: str):
        if DatabaseHandler.get_blacklist_status(interaction.user.id) != 0:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
            )
            return
        if interaction.channel.id != int(os.getenv("DISCORD_SERVER_COMMAND_CHANNEL_ID")):
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="Wrong channel!"
                ),
                ephemeral=True
            )
            return
        try:
            if not re.match(EMAIL_REGEX, email):
                await interaction.response.send_message(
                    embed=EmbedHandler.error(
                        message="Email format is invalid."
                    ),
                    ephemeral=True
                )
                return
            await interaction.response.send_message(
                embed=EmbedHandler.information(
                    message="Check your DMs."
                ),
                ephemeral=True
            )
            await interaction.user.send(
                embed=EmbedHandler.information(
                    message="Checking system..."
                )
            )
            if DatabaseHandler.check_user_exists(interaction.user.id):
                await interaction.user.send(
                    embed=EmbedHandler.warning(
                        message="You already have an account."
                    )
                )
                return
            else:
                await interaction.user.send(
                    embed=EmbedHandler.information(
                        message="Creating account..."
                    )
                )
                password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

                url = f'{os.getenv("PANEL_URL")}/api/application/users'
                headers = {
                    "Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
                print(interaction.user.id)
                print(email)
                payload = {
                    "email": email,
                    "username": str(interaction.user.id),
                    "password": password,
                }

                response = requests.request('POST', url, json=payload, headers=headers)
                print(response.json())
                print(response.status_code)
                if response.status_code == 201:
                    await interaction.user.send(
                        embed=EmbedHandler.success(
                            message=f"Successfully created account.\n"
                                    f"Username: {str(interaction.user.id)}\n"
                                    f"Password: {password}\n"
                                    f"Link: {os.getenv("PANEL_URL")}"
                        )
                    )
                    DatabaseHandler.create_user(interaction.user.id, response.json()['attributes']['id'])
                    Logger.send_webhook(f"{interaction.user.mention} created an account.")
                elif response.status_code == 422:
                    await interaction.user.send(
                        embed=EmbedHandler.warning(
                            message="You already have an account."
                        )
                    )
                else:
                    await interaction.response.send_message(
                        embed=EmbedHandler.error(
                            message="Something went wrong. Please contact support."
                        ),
                        ephemeral=True
                    )
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                embed=EmbedHandler.error(
                    message="Unable to DM you, please open your DMs."
                ),
                ephemeral=True
            )

    @account_command.command(name="info", description="Check the information of your account")
    @app_commands.checks.cooldown(15, 5.0, key=lambda i: i.user.id)
    async def information(self, interaction: discord.Interaction):
        if DatabaseHandler.get_blacklist_status(interaction.user.id) != 0:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
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

            user_information = DatabaseHandler.get_user_info(interaction.user.id)
            server_slots = (user_information[6] or 0) + int(os.getenv("DEFAULT_SERVER_SLOTS") or 0)
            cpu = (user_information[9] or 0) + int(os.getenv("DEFAULT_CPU") or 0)
            ram = (user_information[10] or 0) + int(os.getenv("DEFAULT_RAM") or 0)
            disk = (user_information[11] or 0) + int(os.getenv("DEFAULT_DISK") or 0)
            used_slots = (user_information[7] or 0)
            used_cpu = user_information[12] or 0
            used_ram = user_information[13] or 0
            used_disk = user_information[14] or 0
            coins = (user_information[2] or 0)
            await interaction.response.send_message(
                embed=EmbedHandler.user_information(
                    f"Hello {interaction.user.mention}\n"
                    f"Coins: {coins} coins\n\n"
                    f"CPU: {used_cpu}/{cpu}%\n"
                    f"RAM: {used_ram}/{ram}MB\n"
                    f"Disk: {used_disk}/{disk}MB\n"
                    f"Server slots: {used_slots}/{server_slots} servers."
                )
            )
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                embed=EmbedHandler.error(
                    message="Something went wrong. Please contact support."
                ),
                ephemeral=True
            )

    @information.error
    @create.error
    async def error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Account(bot), guilds=[discord.Object(id=os.getenv("DISCORD_SERVER_ID"))])
