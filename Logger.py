import os
from discord import SyncWebhook
from dotenv import load_dotenv

load_dotenv()

webhook = SyncWebhook.from_url(os.getenv("DISCORD_LOG_WEBHOOK"))

def send_webhook(message):
    webhook.send(
        content=message,
    )
