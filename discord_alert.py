import os
from datetime import datetime

from discord_webhook import DiscordWebhook
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")


def format_time(time_string):
    dt = datetime.fromisoformat(time_string)
    return dt.strftime("%B %-d, %-I:%M %p")


def send_alert(alerts):
    if not WEBHOOK_URL:
        return

    for alert in alerts:
        show = alert["show"]
        seats = alert["seats"]

        message = (
            "🎬 **The Odyssey IMAX 70mm Seats Found!**\n\n"
            f"📍 {show['theatre']}\n"
            f"🕒 {format_time(show['time'])}\n\n"
            "⭐ Best seats:\n"
        )

        for seat in seats[:3]:
            message += f"Row {seat['row']} {seat['seat1']} + {seat['seat2']}\n"

    
        webhook = DiscordWebhook(url=WEBHOOK_URL)
        webhook.content = message
        webhook.execute()