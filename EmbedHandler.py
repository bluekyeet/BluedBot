import os
import discord
from dotenv import load_dotenv

load_dotenv()

def error(message: str) -> discord.Embed:
    embed = discord.Embed(
        title="Error",
        description=message,
        color=discord.Color.red(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=os.getenv("HOST_NAME"))
    return embed


def success(message: str) -> discord.Embed:
    embed = discord.Embed(
        title="Success",
        description=message,
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=os.getenv("HOST_NAME"))
    return embed


def information(message: str) -> discord.Embed:
    embed = discord.Embed(
        title="Info",
        description=message,
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=os.getenv("HOST_NAME"))
    return embed


def warning(message: str) -> discord.Embed:
    embed = discord.Embed(
        title="Warning",
        description=message,
        color=discord.Color.orange(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=os.getenv("HOST_NAME"))
    return embed


def server_information(message) -> discord.Embed:
    embed = discord.Embed(
        title="Server Info",
        description=f"{message}",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=os.getenv("HOST_NAME"))
    return embed


def server_creation(message: str) -> discord.Embed:
    embed = discord.Embed(
        title="Server Creation",
        description=message,
        color=discord.Color.green(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=os.getenv("HOST_NAME"))
    return embed


def user_information(param):
    embed = discord.Embed(
        title="User Info",
        description=param,
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=os.getenv("HOST_NAME"))
    return embed


def help_embed():
    embed = discord.Embed(
        title="Help",
        description="**Manage Account | <#1367445590795092010>**\n"
                    "/createaccount - Create an account.\n"
                    "/userinfo - Check your account information.\n\n"

                    "**Manage Server | <#1367424445886631988>**\n"
                    "/createserver - Create a server.\n"
                    "/serverinfo - Check the information of your server.\n"
                    "/deleteserver - Delete your server.\n"
                    "/renewserver - Renew your server.\n\n"

                    "**Dabloons | <#1367424595824607302>**\n"
                    "/givedabloons - Give dabloons to another user.\n"
                    "/upgradeserver - Upgrade your server.\n"
                    "/linkvertise - Get a linkvertise link to earn dabloons.\n"
                    "/buy - Buy some resources or items.",
        color=discord.Color.blue(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=os.getenv("HOST_NAME"))
    return embed