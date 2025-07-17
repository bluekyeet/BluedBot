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
            if last_renew_date <= int((datetime.datetime.now(datetime.UTC).timestamp()-604800)//1):
                request = requests.post(f"{os.getenv("PANEL_URL")}/api/application/servers/{serverid}/suspend",
                                    headers={"Authorization": f"Bearer {os.getenv('PANEL_KEY')}",
                                            "Accept": "application/json",
                                            "Content-Type": "application/json"})
                if request.status_code == 204:
                    print(f"Server {serverid} suspended.")

        time.sleep(180)