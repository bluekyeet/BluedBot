import os
import random
import time
import databasehandler
import discord
import requests
import datetime
import re
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

SERVERNAME_REGEX = r'^[a-zA-Z0-9 _-]{3,32}$'

def get_random_port(location_id):
    url = f"https://panel.bluedhost.org/api/application/nodes/{location_id}/allocations"
    headers = {
        "Authorization": f"Bearer {os.getenv('PANELKEY')}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    available_allocations = []
    current_page = 1

    while True:
        response = requests.get(f"{url}?page={current_page}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            allocations = data["data"]
            available_allocations.extend(
                [alloc["attributes"]["id"] for alloc in allocations if not alloc["attributes"]["assigned"]]
            )
            pagination = data["meta"]["pagination"]
            if pagination["current_page"] >= pagination["total_pages"]:
                break
            current_page += 1
        else:
            return "No available ports in the specified location."

    if available_allocations:
        return random.choice(available_allocations)
    else:
        return "No available ports in the specified location."

class createserver(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="createserver", description="Create a server on BluedHost.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.choices(location=[app_commands.Choice(name="Hydrogen | India", value=1),
                                    app_commands.Choice(name="Hydrogen | Singapore ", value=5),
                                    app_commands.Choice(name="Gold | India", value=2),
                                    app_commands.Choice(name="Platinum | France", value=3)])
    @app_commands.describe(servername="The name of the server you want to create.", location="The location of the server.")
    async def createserver(self, interaction: discord.Interaction, servername: str, location: app_commands.Choice[int]):
        if interaction.channel.id != 1367424445886631988:
            await interaction.response.send_message(embed=embeds.embed_warning(message="Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning(message="You don't have an account."), ephemeral=True)
                    return
                goldservers = [2]
                if interaction.user.get_role(1368022648168120430) is None and location.value in goldservers:
                    await interaction.response.send_message(embed=embeds.embed_info("You do not currently own BluedHost Gold."), ephemeral=True)
                    return
                if not re.match(SERVERNAME_REGEX, servername):
                    await interaction.response.send_message(embed=embeds.embed_error("Invalid server name. Server names must be 3-32 characters long and can only contain letters, numbers, dashes, and underscores."), ephemeral=True)
                    return
                if not databasehandler.check_if_user_has_slots(interaction.user.id):
                    await interaction.response.send_message(embed=embeds.embed_info("You have used up all your server slots."), ephemeral=True)
                else:
                    await interaction.response.send_message(embed=embeds.embed_server_creation("Creating server..."))
                    if location.value == 3:
                        port = get_random_port(random.choices([3, 4])[0])
                    else:
                        port = get_random_port(location.value)
                    if port == "No available ports in the specified location.":
                        await interaction.edit_original_response(embed=embeds.embed_server_creation("No available ports in the specified location."))
                        return
                    url = 'https://panel.bluedhost.org/api/application/servers'
                    headers = {
                        "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    }
                    payload = {
                      "name": servername,
                      "user": databasehandler.get_user_uid(interaction.user.id),
                      "egg": 1,
                      "docker_image": "ghcr.io/parkervcp/yolks:java_21",
                      "startup": "java -Xms128M -XX:MaxRAMPercentage=95.0 -Dterminal.jline=false -Dterminal.ansi=true -jar {{SERVER_JARFILE}}",
                      "environment": {
                        "BUILD_NUMBER": "latest",
                        "SERVER_JARFILE": "server.jar"
                      },
                      "limits": {
                        "memory": 2048,
                        "swap": 0,
                        "disk": 5120,
                        "io": 500,
                        "cpu": 100
                      },
                      "feature_limits": {
                        "databases": 0,
                        "backups": 0
                      },
                      "allocation": {
                        "default": port
                      }
                    }


                    response = requests.request('POST', url, json=payload, headers=headers)
                    databasehandler.add_server(int(response.json()['attributes']['id']), databasehandler.get_user_uid(interaction.user.id))
                    if response.status_code == 201:
                        try:
                            await interaction.user.send(embed=embeds.embed_server_creation("Successfully created server.\n"
                                                        f"Server Name: {servername}\nLocation: {location.name}\n"
                                                        f"**Resources:**\n"
                                                        f"- Memory: 2GB\n"
                                                        f"- Disk: 5GB\n"
                                                        f"- CPU: 100%\n"
                                                        f"- Link: https://panel.bluedhost.org/server/{response.json()['attributes']['id']}\n"
                                                        f"- Expires in <t:{int((datetime.datetime.now(datetime.UTC).timestamp()//1)+604800)}:R>.\n"
                                                                             f"- /renewserver in <#1367424445886631988> to renew your server."))
                            await interaction.edit_original_response(embed=embeds.embed_server_creation("Server created! Check your DMs for details."))
                        except Exception as e:
                            print(e)
                            await interaction.edit_original_response(embed=embeds.embed_error("Unable to DM you, please open your DMs."))
                            time.sleep(5)
                            await interaction.edit_original_response(embed=embeds.embed_server_creation("Successfully created server.\n"
                                                                             f"Server Name: {servername}\nLocation: {location.name}\n"
                                                                             f"**Resources:**\n"
                                                                             f"- Memory: 2GB\n"
                                                                             f"- Disk: 5GB\n"
                                                                             f"- CPU: 100%\n"
                                                                             f"- Link: https://panel.bluedhost.org/server/{response.json()['attributes']['id']}\n"
                                                                             f"- Expires in <t.{int((datetime.datetime.now(datetime.UTC).timestamp()//1)+604800)}.R>.\n"
                                                                             f"- /renewserver in <#1367424445886631988> to renew your server."))
                    else:
                        await interaction.user.send(embed=embeds.embed_error(message="Something went wrong. Please contact support."))
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error("Unable to DM you, please open your DMs."), ephemeral=True)


    @createserver.error
    async def createserver_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(createserver(bot), guilds=[discord.Object(id=1367424444850634863)])
import discord
import databasehandler
import os
import requests
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, user_id: int, server_id: int):
        super().__init__()
        self.user_id = user_id
        self.server_id = server_id

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger, emoji="❗", custom_id="alert_button")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        await interaction.response.send_message(embed=embeds.embed_success("Server deleted successfully!"))
        response = requests.delete(
            f"https://panel.bluedhost.org/api/application/servers/{self.server_id}",
            headers={
                "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        response.raise_for_status()
        server_info = databasehandler.get_single_server_info(self.server_id)
        server_level = server_info[0]
        databasehandler.delete_server(self.server_id, self.user_id)
        if server_level == 0:
            return
        elif server_level >= 1:
            databasehandler.update_coin_count(interaction.user.id, server_level * 1000)

class deleteserver(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="deleteserver", description="See your server information.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to delete.")
    async def deleteserver(self, interaction: discord.Interaction, server_id: int):
        if interaction.channel.id != 1367424445886631988:
            await interaction.response.send_message(embed=embeds.embed_warning(message="Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning(message="You don't have an account."), ephemeral=True)
                    return
                if not databasehandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                    await interaction.response.send_message(embed=embeds.embed_warning(message="You do not own this server."), ephemeral=True)
                    return
                view = ConfirmDeleteView(interaction.user.id, server_id)
                await interaction.response.send_message(embed=embeds.embed_info("Are you sure you want to delete your server? This action cannot be undone. All purchased upgrades will be refunded. Click 'Yes' to confirm."), view=view)
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error(message="Something went wrong. Please contact support."), ephemeral=True)

    @deleteserver.error
    async def deleteserver_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(deleteserver(bot), guilds=[discord.Object(id=1367424444850634863)])
import os
import discord
import requests
import databasehandler
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

class renewserver(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="renewserver", description="Pay 100 dabloons to renew your server.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to renew.")
    async def renewserver(self, interaction: discord.Interaction, server_id: int):
        if interaction.channel.id != 1367424445886631988:
            await interaction.response.send_message(embed=embeds.embed_warning("Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning("You don't have an account."), ephemeral=True)
                    return
                if not databasehandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                    await interaction.response.send_message(embed=embeds.embed_warning("You are not the owner of this server."), ephemeral=True)
                    return
                coincount = databasehandler.check_coin_count(interaction.user.id)
                if coincount < 100:
                    await interaction.response.send_message(embed=embeds.embed_warning("You don't have enough dabloons to renew your server. You need at least 100 dabloons."))
                    return
                else:
                    databasehandler.update_coin_count(interaction.user.id, -100)
                    databasehandler.renew_server(server_id)
                    await interaction.response.send_message(embed=embeds.embed_success(f"Successfully renewed your server. You have {coincount-100} dabloons left.\nIf your server is suspended, it will be unsuspended within 5-10 minutes."))
                    try:
                        check_suspended_url = f"https://panel.bluedhost.org/api/application/servers/{server_id}"
                        headers = {
                            "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                        }
                        response = requests.get(check_suspended_url, headers=headers)
                        response.raise_for_status()
                        json_data = response.json()
                        server_status = json_data["attributes"]["suspended"]
                        if server_status:
                            server_node = json_data["attributes"]["node"]
                            get_node_url = f"https://panel.bluedhost.org/api/application/nodes/{server_node}"
                            node_response = requests.get(get_node_url, headers=headers)
                            node_response.raise_for_status()
                            node_json_data = node_response.json()
                            node_fqdn = node_json_data["attributes"]["fqdn"]
                            freeze_url = f"http://{node_fqdn}:8888/unfreeze/{server_id}"
                            requests.post(freeze_url, headers=headers)
                            renew_url = f"https://panel.bluedhost.org/api/application/servers/{server_id}/unsuspend"
                            requests.post(renew_url, headers=headers)
                    except Exception as e:
                        print(e)

            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error("Something went wrong. Please contact support."), ephemeral=True)

    @renewserver.error
    async def renewserver_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(renewserver(bot), guilds=[discord.Object(id=1367424444850634863)])

import datetime
import os
import requests
import discord
import Data
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import embeds

load_dotenv()

class serverinfo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="serverinfo", description="See your server information.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to see.")
    async def serverinfo(self, interaction: discord.Interaction, server_id: int = None):
        if interaction.channel.id != 1367424445886631988:
            await interaction.response.send_message(embed=embeds.embed_warning("Wrong channel!"), ephemeral=True)
        else:
            try:
                if not databasehandler.check_user_exists(interaction.user.id) or databasehandler == 400:
                    await interaction.response.send_message(embed=embeds.embed_warning("You don't have an account."), ephemeral=True)
                    return
                if server_id is not None:
                    if not databasehandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                        await interaction.response.send_message(embed=embeds.embed_warning("You don't own that server."), ephemeral=True)
                        return
                    server_info = databasehandler.get_single_server_info(server_id)
                    if server_info == 400:
                        await interaction.response.send_message(embed=embeds.embed_error("Something went wrong. Please contact support."), ephemeral=True)
                        return
                    server_level = server_info[0]
                    server_expire_date = server_info[1]
                    if int(server_expire_date)+604800 == datetime.datetime.now(datetime.UTC).timestamp():
                        server_expire_date = "Expired. Renew with /rewewserver"
                    else:
                        server_expire_date = f"<t:{int(server_expire_date)+604800}:R>"
                    get_server_name_url = f"https://panel.bluedhost.org/api/application/servers/{server[0]}"
                    get_server_info_headers = {
                        "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    }
                    get_server_name_response = requests.get(get_server_name_url, headers=get_server_info_headers)
                    get_server_name_response_json = get_server_name_response.json()
                    server_name = get_server_name_response_json['attributes']['name']
                    await interaction.response.send_message(embed=embeds.embed_server_info(f"- Server Name: {server_name}\n"
                                                            f"- Server ID: {server_id}\n"
                                                            f"- Server Link: https://panel.bluedhost.org/server/{server_id}\n"
                                                            f"- Server Level: {server_level}\n"
                                                            f"- Expiry: {server_expire_date}"))
                else:
                    if not databasehandler.check_if_user_has_any_servers(interaction.user.id):
                        await interaction.response.send_message("You don't have any servers.", ephemeral=True)
                        return
                    server_info = databasehandler.get_all_servers_info(interaction.user.id)
                    if server_info == 400:
                        await interaction.response.send_message("Something went wrong. Please contact support.", ephemeral=True)
                        return
                    server_information = ""
                    for server in server_info:
                        get_server_name_url = f"https://panel.bluedhost.org/api/application/servers/{server[0]}"
                        get_server_info_headers = {
                            "Authorization": f"Bearer {os.getenv('PANELKEY')}",
                            "Accept": "application/json",
                            "Content-Type": "application/json",
                        }
                        get_server_name_response = requests.get(get_server_name_url, headers=get_server_info_headers)
                        get_server_name_response_json = get_server_name_response.json()
                        server_name = get_server_name_response_json['attributes']['name']
                        server_id = server[0]
                        server_level = server[1]
                        server_expire_date = server[2]
                        if int(server_expire_date)+604800 == datetime.datetime.now(datetime.UTC).timestamp():
                            server_expire_date = "Expired. Renew with /renewserver"
                        else:
                            server_expire_date = f"<t:{int(server_expire_date)+604800}:R>"
                        server_information += f"- Server Name: {server_name}\n"
                        server_information += f"- Server ID: {server_id}\n"
                        server_information += f"- Server Level: {server_level}\n"
                        server_information += f"- Expiry: {server_expire_date}\n\n"
                    server_information += f"**Total Servers:** {len(server_info)}"
                    await interaction.response.send_message(embed=embeds.embed_server_info(server_information))
            except Exception as e:
                print(e)
                await interaction.response.send_message(embed=embeds.embed_error("Something went wrong. Please contact support."), ephemeral=True)

    @serverinfo.error
    async def serverinfo_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(serverinfo(bot), guilds=[discord.Object(id=1367424444850634863)])
