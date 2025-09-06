import datetime
import time
from database import DatabaseHandler
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def checker():
    while True:
        servers = DatabaseHandler.get_all_server_expiry_times()
        for serverid, last_renew_date in servers:
            if last_renew_date is None:
                continue
            if last_renew_date <= int((datetime.datetime.now(datetime.timezone.utc).timestamp()-(int(os.getenv("SERVER_RENEW_DAYS"))*86400))//1):
                if last_renew_date == 0:
                    request = requests.post(f"{os.getenv("PANEL_URL")}/api/application/servers/{serverid}/suspend",
                                        headers={"Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
                                                "Accept": "application/json",
                                                "Content-Type": "application/json"})
                    if request.status_code == 204:
                        print(f"Server {serverid} suspended.")
                    DatabaseHandler.suspend_server(serverid)

        time.sleep(180)

def load_system():
    getconfig = DatabaseHandler.get_config()[0]
    system_enabled = os.getenv("SERVER_EXPIRY_SYSTEM", "").lower() == "enable"

    if getconfig == 2:
        DatabaseHandler.update_renew_system(1 if system_enabled else 0)

    elif getconfig == 0 and system_enabled:
        DatabaseHandler.update_renew_system(1)
        DatabaseHandler.update_all_servers_expire()

    elif getconfig == 1 and not system_enabled:
        DatabaseHandler.update_renew_system(0)
