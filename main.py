import telebot
from telebot import types
import os
from flask import Flask, request

TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
ADMIN_ID = 1656900957  # آی‌دی عددی شما

# لینک کانال‌هایی که عضویت در اونها الزامیه
REQUIRED_CHANNELS = [
    "https://t.me/sazemansanjeshe",
    "https://t.me/+aiGGH9GqC8syYjc8",
    "https://t.me/+5G5Kzm5XSs5jOGU0",
    "https://t.me/+rQyIwVnumeJmOWJk",
    "https://t.me/+6KDXytY8iz04MTc0"
]

bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

user_states = {}

# /start command
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    for i, link in enumerate(REQUIRED_CHANNELS, 1):
        markup.add(types.InlineKeyboardButton(f"کانال {i}", url=link))
    markup.add(types.InlineKeyboardButton("✅ عضویت انجام شد", callback_data="check_join"))
    bot.send_message(message.chat.id, "سلام! برای استفاده از ربات تبادل اعضا، ابتدا عضو ۵ کانال زیر شو و سپس روی دکمه عضویت انجام شد کلیک کن:", reply_markup=markup)

# بررسی عضویت (فقط تأیید کاربر - امکان چک عضویت مستقیم نداریم)
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def handle_join_check(call):
    bot.send_message(call.message.chat.id, "✅ عالی! حالا لینک کانال یا گروهت رو بفرست تا برای تبادل بررسی بشه.")
    user_states[call.message.chat.id] = "awaiting_channel_link"

# دریافت لینک کانال از کاربر
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "awaiting_channel_link")
def receive_channel_link(message):
    link = message.text
    if "t.me/" in link:
        bot.send_message(message.chat.id, "🔗 لینک دریافت شد! در حال ارسال به مدیریت جهت بررسی و درج در تبادل...")
        bot.send_message(ADMIN_ID, f"📥 کاربر @{message.from_user.username or message.from_user.first_name} لینک تبادل ارسال کرد:\n\n{link}")
        bot.send_message(message.chat.id, "✅ لینک شما با موفقیت ارسال شد. منتظر تایید ادمین باشید.")
    else:
        bot.send_message(message.chat.id, "❌ لطفاً یک لینک معتبر کانال یا گروه ارسال کن.")
    user_states.pop(message.chat.id, None)

# پشتیبانی از وب‌هوک برای اجرا روی Render
@server.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "OK", 200

@server.route("/", methods=["GET"])
def index():
    return "Bot is running!", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://alpha-bot-zkn3.onrender.com/{TOKEN}")
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
