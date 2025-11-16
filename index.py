import os
import requests
import time

# ==========================
# CONFIGURACIÓN DESDE VARIABLES DE ENTORNO
# ==========================

WHATSAPP_API_KEY = os.getenv("WHATSAPP_API_KEY")
WHATSAPP_PHONE = os.getenv("WHATSAPP_PHONE")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

YOUTUBE_CHANNEL_ID = os.getenv("YOUTUBE_CHANNEL_ID", "UCmbA1iv-7_GLxuqzItMf97A")  # Renzo Tavara
TWITCH_CHANNELS = os.getenv("TWITCH_CHANNELS", "abokeito,ivanelmaster").split(",")

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))  # segundos

# Para evitar spam
last_live_status = {
    "youtube": False
}
for channel in TWITCH_CHANNELS:
    last_live_status[channel] = False

# ==========================
# FUNCIONES
# ==========================

def send_whatsapp(msg):
    url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={msg}&apikey={WHATSAPP_API_KEY}"
    try:
        r = requests.get(url)
        print("WhatsApp respuesta:", r.text)
    except Exception as e:
        print("Error enviando WhatsApp:", e)

def send_discord(msg):
    try:
        r = requests.post(DISCORD_WEBHOOK, json={"content": msg})
        print("Discord status:", r.status_code)
    except Exception as e:
        print("Error enviando Discord:", e)

def is_youtube_live(channel_id):
    url = f"https://mixerno.space/api/youtube-channel-live-status?channelId={channel_id}"
    try:
        r = requests.get(url).json()
        return r.get("isLive", False)
    except:
        return False

def is_twitch_live(username):
    url = f"https://decapi.me/twitch/uptime/{username}"
    try:
        text = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}).text
        return "offline" not in text.lower()
    except:
        return False

# ==========================
# LOOP PRINCIPAL
# ==========================

print("Bot iniciado. Monitoreando directos...")

while True:
    # ---------- YouTube ----------
    youtube_live = is_youtube_live(YOUTUBE_CHANNEL_ID)
    if youtube_live and not last_live_status["youtube"]:
        last_live_status["youtube"] = True
        msg = f"🔴 **Renzo está EN VIVO en YouTube!**\nhttps://www.youtube.com/@renzotavaramarinas770/live"
        send_whatsapp(msg)
        send_discord(msg)
    if not youtube_live:
        last_live_status["youtube"] = False

    # ---------- Twitch ----------
    for channel in TWITCH_CHANNELS:
        twitch_live = is_twitch_live(channel)
        if twitch_live and not last_live_status[channel]:
            last_live_status[channel] = True
            msg = f"🟣 **{channel} está EN VIVO en Twitch!**\nhttps://twitch.tv/{channel}"
            send_whatsapp(msg)
            send_discord(msg)
        if not twitch_live:
            last_live_status[channel] = False

    time.sleep(CHECK_INTERVAL)
