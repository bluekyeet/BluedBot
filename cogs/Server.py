import os
import random
import time
import discord
import requests
import datetime
import re
import EmbedHandler
import Logger
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from database import DatabaseHandler
from eggs.EggLoader import get_egg_by_name, EGG_MODULES, get_egg_by_id
from nodes.NodesLoader import get_node_by_name, NODES, get_node_by_node_id

load_dotenv()

SERVERNAME_REGEX = r'^[a-zA-Z0-9 _-]{3,32}$'

class ConfirmDeleteView(discord.ui.View):
    def __init__(self, user_id: int, server_id: int):
        super().__init__()
        self.user_id = user_id
        self.server_id = server_id

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.danger, emoji="❗", custom_id="alert_button")
    async def confirm_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if DatabaseHandler.get_blacklist_status(interaction.user.id) != 0:
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="You don't have permission to use this command."
                ), ephemeral=True
            )
            return
        if interaction.user.id != self.user_id:
            return
        response = requests.delete(
            f"{os.getenv('PANEL_URL')}/api/application/servers/{self.server_id}",
            headers={
                "Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
        response.raise_for_status()
        if response.status_code == 204:
            await interaction.response.send_message(
                embed=EmbedHandler.success(
                    message="Server deleted successfully!"
                ),
                ephemeral=True
            )
            server_info = DatabaseHandler.get_single_server_info(self.server_id)
            DatabaseHandler.delete_server(self.server_id, self.user_id)
            cpu = server_info[2]
            ram = server_info[3]
            disk = server_info[4]
            DatabaseHandler.update_used_resources(DatabaseHandler.get_user_uid(self.user_id), -int(cpu), -int(ram), -int(disk))
            Logger.send_webhook(f"{interaction.user.mention} deleted server {self.server_id} successfully!")

def get_random_port(location_id):
    url = f"{os.getenv('PANEL_URL')}/api/application/nodes/{location_id}/allocations"
    headers = {
        "Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
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

async def get_egg_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=egg, value=egg)
        for egg in EGG_MODULES
        if current.lower() in egg.lower()
    ]

async def get_node_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name=node, value=node)
        for node in NODES
        if current.lower() in node.lower()
    ]

class Server(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    server_command = app_commands.Group(name="server", description="Server management commands")

    @server_command.command(name="create", description="Create a server on BluedHost.")
    @app_commands.checks.cooldown(5, 10.0, key=lambda i: i.user.id)
    @app_commands.autocomplete(location=get_node_autocomplete, egg=get_egg_autocomplete)
    @app_commands.describe(name="The name of the server you want to create.", location="The location of the server.")
    async def create(self, interaction: discord.Interaction, name: str, location: str, egg: str, cpu: int, ram: int, disk: int):
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
            if not DatabaseHandler.check_user_exists(interaction.user.id) or DatabaseHandler == 400:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You don't have an account."
                    ),
                    ephemeral=True
                )
                return

            if not re.match(SERVERNAME_REGEX, name):
                await interaction.response.send_message(
                    embed=EmbedHandler.error(
                        message="Invalid server name. Server names must be 3-32 characters long and can only contain letters, numbers, dashes, and underscores."
                    ),
                    ephemeral=True
                )
                return

            if not get_egg_by_name(egg):
                await interaction.response.send_message(
                    embed=EmbedHandler.error(
                        message="Invalid egg."
                    ),
                    ephemeral=True
                )
                return

            if not get_node_by_name(location):
                await interaction.response.send_message(
                    embed=EmbedHandler.error(
                        message="Invalid location."
                    ),
                    ephemeral=True
                )
                return

            user_information = DatabaseHandler.get_user_info(interaction.user.id)
            server_slots = (user_information[6] or 0) + int(os.getenv("DEFAULT_SERVER_SLOTS") or 0)
            used_slots = (user_information[7] or 0)

            if server_slots <= used_slots:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="You have used up all your server slots."
                    ),
                    ephemeral=True
                )
                return

            cpu_available = int(user_information[9] or 0) + int(os.getenv("DEFAULT_CPU") or 0)
            ram_available = int(user_information[10] or 0) + int(os.getenv("DEFAULT_RAM") or 0)
            disk_available = int(user_information[11] or 0) + int(os.getenv("DEFAULT_DISK") or 0)
            used_cpu = user_information[12] or 0
            used_ram = user_information[13] or 0
            used_disk = user_information[14] or 0

            if cpu_available-used_cpu-cpu < 0:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="You don't have enough CPU to complete this action."
                    ),
                    ephemeral=True
                )
                return

            if ram_available-used_ram-ram < 0:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="You don't have enough RAM to complete this action."
                    ),
                    ephemeral=True
                )
                return

            if disk_available-used_disk-disk < 0:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="You don't have enough DISK to complete this action."
                    ),
                    ephemeral=True
                )
                return

            if cpu < 10:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="Invalid CPU amount."
                    ),
                    ephemeral=True
                )
                return

            if ram < 64:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="Invalid RAM amount."
                    ),
                    ephemeral=True
                )
                return

            if disk < 128:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="Invalid DISK amount."
                    ),
                    ephemeral=True
                )
                return

            node = get_node_by_name(location)
            if not isinstance(node, tuple) or len(node) != 3:
                raise ValueError(f"Expected a tuple with 3 elements, but got {type(node)}: {node}")

            node_info, eggs_blacklist, node_server_limit = node
            location_id = node_info.get("node_id")
            if location_id is None:
                raise KeyError("Missing 'node_id' in node_info.")

            port = get_random_port(location_id)
            if port == "No available ports in the specified location.":
                raise RuntimeError("No available ports in the specified location.")

            if egg.lower() in eggs_blacklist:
                await interaction.response.send_message(
                    embed=EmbedHandler.error(
                        message="This location doesn't support this egg."
                    ),
                    ephemeral=True
                )
                return

            if port == "No available ports in the specified location.":
                await interaction.response.send_message(
                    embed=EmbedHandler.server_creation(
                        message="No available ports in the specified location."
                    )
                )
                return

            if node_server_limit["cpu"] < cpu:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount % of CPU for a server on this location is {node_server_limit['cpu']}."
                    ),
                    ephemeral=True
                )
                return

            if node_server_limit["ram"] < ram:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount MB of RAM for a server on this location is {node_server_limit['ram']}."
                    ),
                    ephemeral=True
                )
                return

            if node_server_limit["disk"] < disk:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount MB of DISK for a server on this location is {node_server_limit['disk']}."
                    ),
                    ephemeral=True
                )
                return

            egg_func = get_egg_by_name(egg)

            result = egg_func(
                name=name,
                userid=DatabaseHandler.get_user_uid(interaction.user.id),
                memory=ram,
                disk=disk,
                cpu=cpu,
                port=port,
            )

            config, limits = result

            if limits["cpu_max"] < cpu:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount % of CPU for this egg is {limits["cpu_max"]}."
                    ),
                    ephemeral=True
                )
                return

            if limits["memory_max"] < ram:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount MB of RAM for this egg is {limits["memory_max"]}."
                    ),
                    ephemeral=True
                )
                return

            if limits["disk_max"] < disk:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount MB of DISK for this egg is {limits["disk_max"]}."
                    ),
                    ephemeral=True
                )
                return

            await interaction.response.send_message(
                embed=EmbedHandler.server_creation(
                    message="Creating server..."
                )
            )

            url = f'{os.getenv("PANEL_URL")}/api/application/servers'
            headers = {
                "Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
                'Accept': 'Application/vnd.pterodactyl.v1+json',
                "Content-Type": "application/json"
            }

            response = requests.request('POST', url, json=config, headers=headers)
            if response.status_code == 201:
                Logger.send_webhook(f"{interaction.user.mention} has created server with ID of {int(response.json()['attributes']['id'])}, {cpu}% CPU, {ram}MB RAM, and {disk}MB DISK.")
                DatabaseHandler.add_server(int(response.json()['attributes']['id']), DatabaseHandler.get_user_uid(interaction.user.id), cpu, ram, disk)
                if os.getenv("SERVER_EXPIRY_SYSTEM").lower() == "enable":
                    embed=EmbedHandler.server_creation(
                        "Successfully created server.\n"
                        f"Server Name: {name}\n"
                        f"Location: {location}\n"
                        f"**Resources:**\n"
                        f"- CPU: {cpu}%\n"
                        f"- RAM: {ram}MB\n"
                        f"- DISK: {disk}MB\n"
                        f"- Link: {os.getenv('PANEL_URL')}/server/{response.json()['attributes']['id']}\n"
                        f"- Expires in <t:{int((datetime.datetime.now(datetime.UTC).timestamp()//1)+(int(os.getenv('SERVER_RENEW_DAYS'))*86400))}:R>.\n"
                        f"- /renewserver in <#{os.getenv('DISCORD_SERVER_COMMAND_CHANNEL_ID')}> to renew your server."
                    )
                else:
                    embed = EmbedHandler.server_creation(
                        "Successfully created server.\n"
                        f"Server Name: {name}\n"
                        f"Location: {location}\n"
                        f"**Resources:**\n"
                        f"- CPU: {cpu}%\n"
                        f"- RAM: {ram}MB\n"
                        f"- DISK: {disk}MB\n"
                        f"- Link: {os.getenv('PANEL_URL')}/server/{response.json()['attributes']['id']}\n"
                    )
                try:
                    await interaction.user.send(
                        embed=embed
                    )
                    await interaction.edit_original_response(embed=EmbedHandler.server_creation("Server created! Check your DMs for details."))
                except Exception as e:
                    print(e)
                    await interaction.edit_original_response(embed=EmbedHandler.error("Unable to DM you, please open your DMs."))
                    time.sleep(5)
                    await interaction.edit_original_response(embed=embed)
            else:
                print(response.json())
                print(response.status_code)
                await interaction.user.send(
                    embed=EmbedHandler.error(
                        message="Something went wrong. Please contact support."
                    )
                )
                return
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                embed=EmbedHandler.error(
                    message="Unable to DM you, please open your DMs."
                ),
                ephemeral=True
            )
            return

    @server_command.command(name="delete", description="Delete a specific server.")
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to delete.")
    async def delete(self, interaction: discord.Interaction, server_id: int):
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
            if not DatabaseHandler.check_user_exists(interaction.user.id) or DatabaseHandler == 400:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You don't have an account."
                    ),
                    ephemeral=True
                )
                return
            if not DatabaseHandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You do not own this server."
                    ),
                    ephemeral=True
                )
                return
            view = ConfirmDeleteView(interaction.user.id, server_id)
            await interaction.response.send_message(
                embed=EmbedHandler.information(
                    message="Are you sure you want to delete your server? This action cannot be undone.\nAll resources will be refunded. Click 'Yes' to confirm."
                ),
                view=view
            )
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                embed=EmbedHandler.error(
                    message="Something went wrong. Please contact support."
                ),
                ephemeral=True
            )
            return

    @server_command.command(name="renew", description="Pay coins to renew your server.")
    @app_commands.checks.cooldown(5, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to renew.")
    async def renew(self, interaction: discord.Interaction, server_id: int):
        if os.getenv("SERVER_EXPIRY_SYSTEM").lower() != "enable":
            await interaction.response.send_message(
                embed=EmbedHandler.warning(
                    message="Server expiry is disabled."
                ),
                ephemeral=True
            )
            return
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
            if not DatabaseHandler.check_user_exists(interaction.user.id) or DatabaseHandler == 400:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You don't have an account."
                    ),
                    ephemeral=True
                )
                return
            if not DatabaseHandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You are not the owner of this server."
                    ),
                    ephemeral=True
                )
                return
            coincount = DatabaseHandler.check_coin_count(interaction.user.id)
            if coincount < int(os.getenv("SERVER_RENEW_PRICE")):
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message=f"You don't have enough coins to renew your server. You need at least {os.getenv('SERVER_RENEW_PRICE')} coins."
                    ),
                    ephemeral=True
                )
                return
            else:
                DatabaseHandler.update_coin_count(interaction.user.id, -int(os.getenv("SERVER_RENEW_PRICE")))
                DatabaseHandler.renew_server(server_id)
                Logger.send_webhook(f"{interaction.user.mention} renewed their server with id of {server_id}")
                await interaction.response.send_message(
                    embed=EmbedHandler.success(
                        message=f"Successfully renewed your server. You have {coincount - int(os.getenv('SERVER_RENEW_PRICE'))} coins left.\n"
                                f"If your server is suspended, it will be unsuspended within 5-10 minutes."
                    )
                )
                try:
                    check_suspended_url = f"{os.getenv('PANEL_URL')}/api/application/servers/{server_id}"
                    headers = {
                        "Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    }
                    response = requests.get(check_suspended_url, headers=headers)
                    response.raise_for_status()
                    json_data = response.json()
                    server_status = json_data["attributes"]["suspended"]
                    if server_status:
                        renew_url = f"https://panel.bluedhost.org/api/application/servers/{server_id}/unsuspend"
                        requests.post(renew_url, headers=headers)
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                embed=EmbedHandler.error(
                    message="Something went wrong. Please contact support."
                ),
                ephemeral=True
            )
            return

    @server_command.command(name="info", description="See your server information.")
    @app_commands.checks.cooldown(5, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to see.")
    async def information(self, interaction: discord.Interaction, server_id: int = None):
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
            if not DatabaseHandler.check_user_exists(interaction.user.id) or DatabaseHandler == 400:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You don't have an account."
                    ),
                    ephemeral=True
                )
                return
            if server_id is not None:
                if not DatabaseHandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You don't own that server."
                        ),
                        ephemeral=True
                    )
                    return
                server_info = DatabaseHandler.get_single_server_info(server_id)
                if server_info == 400:
                    await interaction.response.send_message(
                        embed=EmbedHandler.error(
                            message="Something went wrong. Please contact support."
                        ),
                        ephemeral=True
                    )
                    return
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="Loading your server's information..."
                    )
                )
                server_expire_date = server_info[1]
                if os.getenv('SERVER_EXPIRY_SYSTEM').lower() == "enable":
                    if int(server_expire_date) + (int(os.getenv("SERVER_RENEW_DAYS"))*86400) == datetime.datetime.now(datetime.UTC).timestamp():
                        server_expire_date = "\n- Expiry: Expired. Renew with /rewewserver"
                    else:
                        server_expire_date = f"\n- Expiry: <t:{int(server_expire_date) + (int(os.getenv("SERVER_RENEW_DAYS"))*86400)}:R>"
                else:
                    server_expire_date = ""
                get_server_name_url = f"{os.getenv('PANEL_URL')}/api/application/servers/{server_id}"
                get_server_info_headers = {
                    "Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                }
                get_server_name_response = requests.get(get_server_name_url, headers=get_server_info_headers)
                get_server_name_response_json = get_server_name_response.json()
                server_name = get_server_name_response_json['attributes']['name']
                await interaction.edit_original_response(
                    embed=EmbedHandler.server_information(
                        f"- Server Name: {server_name}\n"
                        f"- Server ID: {server_id}\n"
                        f"- Server Link: https://panel.bluedhost.org/server/{server_id}\n"
                        f"- CPU: {server_info[2]}%\n"
                        f"- RAM: {server_info[3]}MB\n"
                        f"- DISK: {server_info[4]}MB"
                        f"{server_expire_date}"
                    )
                )
            else:
                if not DatabaseHandler.check_if_user_has_any_servers(interaction.user.id):
                    await interaction.response.send_message(
                        embed=EmbedHandler.warning(
                            message="You don't have any servers."
                        ),
                        ephemeral=True
                    )
                    return
                server_info = DatabaseHandler.get_all_servers_info(interaction.user.id)
                if server_info == 400:
                    await interaction.response.send_message(
                        embed=EmbedHandler.error(
                            message="Something went wrong. Please contact support."
                        ),
                        ephemeral=True
                    )
                    return
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="Loading all your servers' information..."
                    )
                )
                server_information = ""
                for server in server_info:
                    get_server_name_url = f"{os.getenv('PANEL_URL')}/api/application/servers/{server[0]}"
                    get_server_info_headers = {
                        "Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
                        "Accept": "application/json",
                        "Content-Type": "application/json",
                    }
                    get_server_name_response = requests.get(get_server_name_url, headers=get_server_info_headers)
                    get_server_name_response_json = get_server_name_response.json()
                    server_name = get_server_name_response_json['attributes']['name']
                    server_id = server[0]
                    server_expire_date = server[2]
                    if os.getenv('SERVER_EXPIRY_SYSTEM').lower() == "enable":
                        if int(server_expire_date) + (
                                int(os.getenv("SERVER_RENEW_DAYS")) * 86400) == datetime.datetime.now(
                                datetime.UTC).timestamp():
                            server_expire_date = "\n- Expiry: Expired. Renew with /rewewserver"
                        else:
                            server_expire_date = f"\n- Expiry: <t:{int(server_expire_date) + (int(os.getenv("SERVER_RENEW_DAYS")) * 86400)}:R>"
                    else:
                        server_expire_date = ""
                    server_information += f"- Server Name: {server_name}\n"
                    server_information += f"- Server ID: {server_id}\n"
                    server_information += f"- CPU: {server[2]}%\n"
                    server_information += f"- RAM: {server[3]}MB\n"
                    server_information += f"- DISK: {server[4]}MB"
                    server_information += f"{server_expire_date}\n"
                server_information += f"**Total Servers:** {len(server_info)}"
                await interaction.edit_original_response(embed=EmbedHandler.server_information(server_information))
        except Exception as e:
            print(e)
            await interaction.response.send_message(
                embed=EmbedHandler.error(
                    message="Something went wrong. Please contact support."
                ),
                ephemeral=True
            )
            return

    @server_command.command(name="edit", description="Edit resources of your server.")
    @app_commands.checks.cooldown(5, 10.0, key=lambda i: i.user.id)
    @app_commands.describe(server_id="The ID of the server you want to edit.")
    async def edit(self, interaction: discord.Interaction, server_id: int, cpu: int = None, ram: int = None, disk: int = None):
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
            if not DatabaseHandler.check_user_exists(interaction.user.id) or DatabaseHandler == 400:
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You don't have an account."
                    ),
                    ephemeral=True
                )
                return

            if not DatabaseHandler.check_if_user_owns_that_server(interaction.user.id, server_id):
                await interaction.response.send_message(
                    embed=EmbedHandler.warning(
                        message="You don't own that server."
                    ),
                    ephemeral=True
                )
                return

            server_info = DatabaseHandler.get_single_server_info(server_id)
            using_cpu = server_info[2]
            using_ram = server_info[3]
            using_disk = server_info[4]

            user_information = DatabaseHandler.get_user_info(interaction.user.id)
            cpu_available = (user_information[9] or 0) + int(os.getenv("DEFAULT_CPU") or 0)
            ram_available = (user_information[10] or 0) + int(os.getenv("DEFAULT_RAM") or 0)
            disk_available = (user_information[11] or 0) + int(os.getenv("DEFAULT_DISK") or 0)

            used_cpu = user_information[12] or 0
            used_ram = user_information[13] or 0
            used_disk = user_information[14] or 0

            if cpu is None:
                cpu = using_cpu
            if ram is None:
                ram = using_ram
            if disk is None:
                disk = using_disk

            if cpu < 10:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="Invalid CPU amount."
                    ),
                    ephemeral=True
                )
                return

            if ram < 64:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="Invalid RAM amount."
                    ),
                    ephemeral=True
                )
                return

            if disk < 128:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="Invalid DISK amount."
                    ),
                    ephemeral=True
                )
                return

            if used_cpu - using_cpu + cpu > cpu_available:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="You don't have enough CPU to complete this action."
                    ),
                    ephemeral=True
                )
                return

            if used_ram - using_ram + ram > ram_available:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="You don't have enough RAM to complete this action."
                    ),
                    ephemeral=True
                )
                return

            if used_disk - using_disk + disk > disk_available:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message="You don't have enough DISK to complete this action."
                    ),
                    ephemeral=True
                )
                return

            get_information_number_url = f"{os.getenv('PANEL_URL')}/api/application/servers/{server_id}"
            get_information_number_headers = {
                "Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            get_information = requests.get(url=get_information_number_url, headers=get_information_number_headers)
            get_information_json = get_information.json()
            allocation_id = get_information_json['attributes']['allocation']
            location = get_information_json['attributes']['location']
            egg = get_information_json['attributes']['egg']

            node = get_node_by_node_id(location)
            node_info, eggs_blacklist, node_server_limit = node

            if node_server_limit["cpu"] < cpu:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount % of CPU for a server on this location is {node_server_limit['cpu']}."
                    ),
                    ephemeral=True
                )
                return

            if node_server_limit["ram"] < ram:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount MB of RAM for a server on this location is {node_server_limit['ram']}."
                    ),
                    ephemeral=True
                )
                return

            if node_server_limit["disk"] < disk:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount MB of DISK for a server on this location is {node_server_limit['disk']}."
                    ),
                    ephemeral=True
                )
                return

            egg_func = get_egg_by_id(egg)

            result = egg_func(
                name="placeholder",
                userid=0,
                memory=ram,
                disk=disk,
                cpu=cpu,
                port=0,
            )

            config, limits = result

            if limits["cpu_max"] < cpu:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount % of CPU for this egg is {limits["cpu_max"]}."
                    ),
                    ephemeral=True
                )
                return

            if limits["memory_max"] < ram:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount MB of RAM for this egg is {limits["memory_max"]}."
                    ),
                    ephemeral=True
                )
                return

            if limits["disk_max"] < disk:
                await interaction.response.send_message(
                    embed=EmbedHandler.information(
                        message=f"The maximum amount MB of DISK for this egg is {limits["disk_max"]}."
                    ),
                    ephemeral=True
                )
                return

            await interaction.response.send_message(
                embed=EmbedHandler.information(
                    message="Editing server resources..."
                )
            )

            DatabaseHandler.update_used_resources(DatabaseHandler.get_user_uid(interaction.user.id), -using_cpu + cpu, -using_ram + ram, -using_disk + disk)
            DatabaseHandler.edit_server(server_id, cpu, ram, disk)

            url = f"{os.getenv('PANEL_URL')}/api/application/servers/{server_id}/build"
            headers = {
                "Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            payload = {
                "allocation": allocation_id,
                "memory": ram,
                "swap": -1,
                "disk": disk,
                "io": 500,
                "cpu": cpu,
                "feature_limits": {
                    "databases": 0,
                    "backups": 0
                }
            }
            requests.patch(url=url, json=payload, headers=headers)
            await interaction.edit_original_response(
                embed=EmbedHandler.success(
                    f"**Edited server**\n"
                    f"- Server ID: {server_id}\n"
                    f"- CPU: {cpu}%\n"
                    f"- RAM: {ram}MB\n"
                    f"- DISK: {disk}MB"
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
            return

    @renew.error
    @create.error
    @information.error
    @delete.error
    @edit.error
    async def error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                f"This command is on cooldown. Please try again in {error.retry_after:.2f} seconds.",
                ephemeral=True
            )
        else:
            raise error


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Server(bot), guilds=[discord.Object(id=os.getenv("DISCORD_SERVER_ID"))])
