import os
import discord
from database import DatabaseHandler
import EmbedHandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

class Coins(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="addcoins", description="Add an amount of coins to a specific user.")
    @app_commands.describe(user="The Discord user of the person you want to add coins to.", amount="The amount of coins you want to add to an user.")
    async def addcoins(self, interaction: discord.Interaction, user: discord.User, amount: int):
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
            except Exception as e:
                print(e)
                await interaction.response.send_message(
                    embed=EmbedHandler.error(
                        message="Something went wrong. Please contact support."
                    ),
                    ephemeral=True
                )

    @app_commands.command(name="buy", description="Purchase resources for your server.")
    @app_commands.checks.cooldown(10, 5.0, key=lambda i: i.user.id)
    @app_commands.choices(item=[app_commands.Choice(name="Server slot | 500 coins", value=1)])
    @app_commands.describe(item="The item you want to buy.")
    async def buy(self, interaction: discord.Interaction, item: app_commands.Choice[int]):
        if interaction.channel.id != int(os.getenv("DISCORD_SERVER_COMMAND_CHANNEL_ID")):
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="Wrong channel!"
                ),
                ephemeral=True
            )
        else:
            try:
                if os.getenv("SHOP_SYSTEM").lower() != "enable":
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="Shop are currently disabled."
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
                user_information = DatabaseHandler.get_user_info(interaction.user.id)
                coins = user_information[2]
                if item.value == 1:
                    if coins >= 500:
                        DatabaseHandler.update_coin_count(interaction.user.id, -500)
                        DatabaseHandler.update_server_slots(interaction.user.id, 1)
                        await interaction.response.send_message(
                            embed=EmbedHandler.success(
                                message=f"You have bought a server slot for 500 coins.\nYou now have {coins - 500} coins left."
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

    @app_commands.command(name="boostrewards", description="Claim your boost rewards.")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.user.id)
    async def boostrewards(self, interaction: discord.Interaction):
        if interaction.channel.id != int(os.getenv("DISCORD_SERVER_COMMAND_CHANNEL_ID")):
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="Wrong channel!"
                ),
                ephemeral=True
            )
        else:
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
                DatabaseHandler.update_coin_count(interaction.user.id, int(os.getenv("DISCORD_BOOST_REWARD_COINS")))
                DatabaseHandler.update_boost_rewards_claimed(interaction.user.id, 1)
                await interaction.response.send_message(
                    embed=EmbedHandler.success(
                        message="You have successfully claimed your boost reward of 1500 coins."
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
