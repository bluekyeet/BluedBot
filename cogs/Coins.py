import os
import discord
import Logger
from database import DatabaseHandler
import EmbedHandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class Coins(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="shop", description="Purchase resources for your server.")
    @app_commands.checks.cooldown(10, 5.0, key=lambda i: i.user.id)
    @app_commands.choices(item=[app_commands.Choice(name=f"Server slot | {os.getenv('SERVER_SLOT_PRICE')} coins", value=1),
                                app_commands.Choice(name=f"CPU (per 100%) | {os.getenv('CPU_PRICE')} coins", value=2),
                                app_commands.Choice(name=f"RAM (per 1024 MB) | {os.getenv('RAM_PRICE')} coins", value=3),
                                app_commands.Choice(name=f"DISK (per 1024 MB) | {os.getenv('DISK_PRICE')} coins", value=4)])
    @app_commands.describe(item="The item you want to buy.")
    async def buy(self, interaction: discord.Interaction, item: app_commands.Choice[int]):
        if DatabaseHandler.get_blacklist_status(interaction.user.id) != 0:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
            )
            return
        if os.getenv("SHOP_SYSTEM").lower() != "enable":
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="Shop are currently disabled."
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
            return
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
            coins = user_information[2]
            server_slot_price = int(os.getenv("SERVER_SLOT_PRICE"))
            server_slots = (int(user_information[6]) or 0)
            cpu = (int(user_information[9]) or 0)
            ram = (int(user_information[10]) or 0)
            disk = (int(user_information[11]) or 0)
            cpu_price = int(os.getenv("CPU_PRICE"))
            ram_price = int(os.getenv("RAM_PRICE"))
            disk_price = int(os.getenv("DISK_PRICE"))
            if item.value == 1:
                if server_slots >= int(os.getenv("SERVER_SLOT_LIMIT")):
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You have reached the maximum amount purchasable of server slots."
                        )
                    )
                    return
                if coins >= server_slot_price:
                    Logger.send_webhook(f"{interaction.user.mention} bought a server slot.")
                    DatabaseHandler.update_coin_count(interaction.user.id, -server_slot_price)
                    DatabaseHandler.update_server_slots(interaction.user.id, 1)
                    await interaction.response.send_message(
                        embed=EmbedHandler.success(
                            message=f"You have bought a server slot for {server_slot_price} coins.\n"
                                    f"You now have {coins - server_slot_price} coins left."
                        )
                    )
                    return
                else:
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You don't have enough coins to purchase this item."
                        ),
                        ephemeral=True
                    )
                    return
            elif item.value == 2:
                if cpu >= int(os.getenv("CPU_LIMIT")):
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You have reached the maximum amount purchasable of CPU."
                        )
                    )
                    return
                if coins >= cpu_price:
                    Logger.send_webhook(f"{interaction.user.mention} bought 100% CPU.")
                    DatabaseHandler.update_coin_count(interaction.user.id, -cpu_price)
                    DatabaseHandler.update_cpu(interaction.user.id, 1)
                    await interaction.response.send_message(
                        embed=EmbedHandler.success(
                            message=f"You have bought 100% CPU for {cpu_price} coins.\n"
                                    f"You now have {coins - cpu_price} coins left."
                        )
                    )
                else:
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You don't have enough coins to purchase this item."
                        ),
                        ephemeral=True
                    )
                    return
            elif item.value == 3:
                if ram >= int(os.getenv("RAM_LIMIT")):
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You have reached the maximum amount purchasable of RAM."
                        )
                    )
                    return
                if coins >= ram_price:
                    Logger.send_webhook(f"{interaction.user.mention} bought 1024MB RAM")
                    DatabaseHandler.update_coin_count(interaction.user.id, -ram_price)
                    DatabaseHandler.update_cpu(interaction.user.id, 1)
                    await interaction.response.send_message(
                        embed=EmbedHandler.success(
                            message=f"You have bought 1024 MB of RAM for {ram_price} coins.\n"
                                    f"You now have {coins - ram_price} coins left."
                        )
                    )
                else:
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You don't have enough coins to purchase this item."
                        ),
                        ephemeral=True
                    )
                    return
            elif item.value == 4:
                if disk >= int(os.getenv("DISK_LIMIT")):
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You have reached the maximum amount purchasable of DISK."
                        )
                    )
                    return
                if coins >= disk_price:
                    Logger.send_webhook(f"{interaction.user.mention} bought 1024 MB DISK.")
                    DatabaseHandler.update_coin_count(interaction.user.id, -disk_price)
                    DatabaseHandler.update_cpu(interaction.user.id, 1)
                    await interaction.response.send_message(
                        embed=EmbedHandler.success(
                            message=f"You have bought 1024 MB of DISK for {disk_price} coins.\n"
                                    f"You now have {coins - disk_price} coins left."
                        )
                    )
                else:
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You don't have enough coins to purchase this item."
                        ),
                        ephemeral=True
                    )
                    return
            else:
                await interaction.response.send_message(
                    embed=EmbedHandler.error(
                        message="Something went wrong. Please contact support."
                    ),
                    ephemeral=True
                )
                return
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                embed=EmbedHandler.error(
                    message="Something went wrong. Please contact support."
                ),
                ephemeral=True
            )
            return

    @app_commands.command(name="boostrewards", description="Claim your boost rewards.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def boostrewards(self, interaction: discord.Interaction):
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
            if os.getenv("DISCORD_BOOST_REWARD_SYSTEM").lower() != "enable":
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="Boost rewards are currently disabled."
                    ),
                    ephemeral=True
                )
                return
            if not DatabaseHandler.check_user_exists(interaction.user.id) or DatabaseHandler == 400:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You don't have an account."
                    ),
                    ephemeral=True
                )
                return
            if interaction.user.premium_since is None:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You need to boost the server to claim the reward."
                    ),
                    ephemeral=True
                )
                return
            if DatabaseHandler.boost_rewards_claimed(interaction.user.id) == 1:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You have already claimed your boost reward."
                    ),
                    ephemeral=True
                )
                return
            Logger.send_webhook(f"{interaction.user.mention} claimed their boost reward.")
            DatabaseHandler.update_coin_count(interaction.user.id, int(os.getenv("DISCORD_BOOST_REWARD_COINS")))
            DatabaseHandler.update_boost_rewards_claimed(interaction.user.id, 1)
            await interaction.response.send_message(
                embed=EmbedHandler.success(
                    message=f'You have successfully claimed your boost reward of {os.getenv("discord_boost_reward_coins")} coins.'
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

    @app_commands.command(name="givecoins", description="Give an amount of coins to another user.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(user="The user you want to give coins to", amount="The amount of coins you want to give")
    async def givecoins(self, interaction: discord.Interaction, user: discord.User, amount: int):
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
                    embed=EmbedHandler.information(
                        message="You don't have an account."
                    ),
                    ephemeral=True
                )
                return
            if not DatabaseHandler.check_user_exists(user.id) or DatabaseHandler == 400:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="The person you are trying to give coins to does not have an account."
                    ),
                    ephemeral=True
                )
                return
            if amount <= 0:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You cannot give a person negative or zero coins."
                    ),
                    ephemeral=True
                )
                return
            if DatabaseHandler.check_coin_count(interaction.user.id) < amount:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message=f"You do not have enough coins to give {DatabaseHandler.check_coin_count(interaction.user.id)} coins."
                    ),
                    ephemeral=True
                )
                return
            Logger.send_webhook(f"{interaction.user.mention} gave {amount} coins to {user.mention}.")
            DatabaseHandler.update_coin_count(interaction.user.id, -amount)
            DatabaseHandler.update_coin_count(user.id, amount)
            await interaction.response.send_message(
                embed=EmbedHandler.success(
                    message=f"You have successfully given {amount} coins to <@{user.id}>.\n"
                            f"You now have {DatabaseHandler.check_coin_count(interaction.user.id)} coins left."
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

    @givecoins.error
    @buy.error
    @boostrewards.error
    async def error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Coins(bot), guilds=[discord.Object(id=os.getenv("DISCORD_SERVER_ID"))])
