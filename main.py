import telebot
import requests
from telebot import types
import os
from flask import Flask
from threading import Thread

app = Flask('')

# --- CONFIGURATION ---
TOKEN = "8230723230:AAGZhHB9gEDoKbmXF_aWJ5lAFXjVWCkw_pI"
bot = telebot.TeleBot(TOKEN, threaded=False)
ADMIN_ID = 8157596960

API_KEYS = {
    "CPM1": "AIzaSyBW1ZbMiUeDZHYUO2bY8Bfnf5rRgrQGPTM", 
    "CPM2": "AIzaSyCQDz9rgjgmvmFkvVfmvr2-7fT4tfrzRRQ"
}

user_sessions = {}

@app.route('/')
def home():
    return "Bot is Running"

# ലോഗിൻ, എഡിറ്റിംഗ് തുടങ്ങിയ നിങ്ങളുടെ ബാക്കി എല്ലാ ഫംഗ്ഷനുകളും (start, login_start etc.) ഇവിടെ ചേർക്കുക...
# (നിങ്ങളുടെ പഴയ കോഡ് ഇവിടെ വേണം)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # ബോട്ടിനെ ഒരു സെപ്പറേറ്റ് ത്രെഡിൽ റൺ ചെയ്യുന്നു
    Thread(target=run_bot).start()
    # പോർട്ട് Render നൽകുന്നത് ഉപയോഗിക്കുന്നു
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
