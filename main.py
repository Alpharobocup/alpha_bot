import telebot
from telebot import types
import os
from flask import Flask, request

API_TOKEN = os.getenv("BOT_TOKEN", "7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo")

bot = telebot.TeleBot(API_TOKEN)
user_states = {}

# دکمه شروع برای تست
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("بررسی عضویت", callback_data="check_join"))
    bot.send_message(message.chat.id, "سلام! برای ادامه لطفاً عضویتت در کانال رو بررسی کن:", reply_markup=markup)

# بررسی عضویت کاربر در کانال
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def handle_join_check(call):
    user_id = call.from_user.id
    all_joined = True
    failed_channels = []

    channel_usernames = [
        "@alpha20288",  # کانال‌های مورد نیاز برای عضویت
    ]

    for username in channel_usernames:
        try:
            member = bot.get_chat_member(username, user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                all_joined = False
                failed_channels.append(username)
        except Exception as e:
            all_joined = False
            failed_channels.append(username)

    if all_joined:
        bot.send_message(call.message.chat.id, "✅ عالی! حالا لینک کانال یا گروهت رو بفرست تا برای تبادل بررسی بشه.")
        user_states[call.message.chat.id] = "awaiting_channel_link"
    else:
        bot.send_message(call.message.chat.id, "❌ برای ادامه باید توی همه کانال‌ها عضو باشی. لطفاً عضو شو و دوباره تلاش کن.")

# دریافت لینک کاربر
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == "awaiting_channel_link")
def receive_channel_link(message):
    channel_link = message.text
    bot.send_message(message.chat.id, f"✅ لینک '{channel_link}' دریافت شد و در حال بررسی است.")
    user_states[message.chat.id] = None

# تنظیمات وب‌هوک برای اجرای روی Render یا سرور
app = Flask(__name__)

@app.route('/')
def index():
    return "ربات در حال اجراست!"

@app.route('/' + API_TOKEN, methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return '', 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://alpha-bot-zkn3.onrender.com/{API_TOKEN}")
    app.run(host="0.0.0.0", port=port)
