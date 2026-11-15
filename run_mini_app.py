# -*- coding: utf-8 -*-
"""
run_mini_app.py
1. Starts local HTTP server on port 8080 serving index.html
2. Launches cloudflared tunnel to expose https://xxx.trycloudflare.com
3. Starts aiogram bot with Open App WebApp button and sets chat menu button
"""

import os
import sys
import time
import json
import asyncio
import logging
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    WebAppInfo, 
    MenuButtonWebApp,
    Message
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = r"C:\Users\user\.gemini\antigravity\scratch"
BOT_TOKEN = "9117993446:AAE4Uf-uMKFdoqVwxE17BxTzOXu1Xuuhr08"

class PlatformHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)
    
    def log_message(self, format, *args):
        pass # Quiet logging

def start_http_server():
    server = HTTPServer(("127.0.0.1", 8080), PlatformHandler)
    logger.info("Local HTTP server running on http://127.0.0.1:8080")
    server.serve_forever()

tunnel_url = None

def start_cloudflared():
    global tunnel_url
    cmd = ["cloudflared", "tunnel", "--url", "http://127.0.0.1:8080"]
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1)
    
    for line in proc.stderr:
        if "trycloudflare.com" in line:
            import re
            m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
            if m:
                tunnel_url = m.group(0)
                logger.info(f"Cloudflare Tunnel URL: {tunnel_url}")
                break

# Thread for HTTP server
t1 = threading.Thread(target=start_http_server, daemon=True)
t1.start()

# Thread for Cloudflare
t2 = threading.Thread(target=start_cloudflared, daemon=True)
t2.start()

# Wait for tunnel URL
print("Waiting for Cloudflare Tunnel URL...")
for _ in range(30):
    if tunnel_url:
        break
    time.sleep(1)

if not tunnel_url:
    print("Could not obtain Tunnel URL!")
    sys.exit(1)

print(f"READY! WebApp URL is: {tunnel_url}")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Open App (Platformani Ochish)", web_app=WebAppInfo(url=tunnel_url))]
    ])
    text = (
        f"👋 **Assalomu alaykum, {message.from_user.first_name}!**\n\n"
        f"🏛️ **Cyber University • Oraliq Nazorat Telegram Mini App**iga xush kelibsiz!\n\n"
        f"📱 Testlar, formulalar, konspektlar va shaxsiy kabinetingiz to'liq **Telegram ilovasi (Mini App)** sifatida ishga tushirildi.\n\n"
        f"Ilovani ochish uchun pastdagi **'Open App'** tugmasini bosing:"
    )
    await message.answer(text, reply_markup=kb, parse_mode="Markdown")

async def main():
    # Set chat menu button to WebApp Open App
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(text="Open App", web_app=WebAppInfo(url=tunnel_url))
        )
        logger.info(f"Telegram MenuButton 'Open App' set successfully to {tunnel_url}")
    except Exception as e:
        logger.warning(f"Could not set menu button: {e}")
        
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
