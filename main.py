import telebot
from flask import Flask, request
import random
import os

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo' 
WEBHOOK_URL = 'https://alpha-bot-zkn3.onrender.com'  # آدرس سایتت رو بزن

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# ✳️ خوش‌آمدگویی
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_user in message.new_chat_members:
        name = new_user.first_name or "کاربر جدید"
        bot.send_message(message.chat.id, f"🌟 خوش اومدی {name}!")

# ✳️ حذف پیام‌های سیستمی (join/leave/change)
@bot.message_handler(content_types=['left_chat_member', 'new_chat_title', 'new_chat_photo', 'pinned_message'])
def delete_system_messages(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

# ✳️ دستور شماره رندوم
@bot.message_handler(commands=['number'])
def random_number(message):
    operator = random.choice(["0912", "0935", "0930", "0990", "0919", "0936"])
    number = operator + "".join(random.choices("0123456789", k=7))
    bot.reply_to(message, f"📱 شماره تصادفی:\n`{number}`", parse_mode="Markdown")

# ✳️ اعلام ادمین‌ها و مالک
@bot.message_handler(commands=['admins'])
def send_admins_list(message):
    try:
        chat_id = message.chat.id
        admins = bot.get_chat_administrators(chat_id)
        msg = "👑 لیست ادمین‌ها:\n"
        for admin in admins:
            user = admin.user
            if admin.status == 'creator':
                msg += f"🌟 مالک: {user.first_name}\n"
            else:
                msg += f"▫️ {user.first_name}\n"
        bot.reply_to(message, msg)
    except Exception as e:
        bot.reply_to(message, "خطا در گرفتن لیست ادمین‌ها.")

# ✳️ صفحه خانه برای تست
@app.route('/', methods=['GET'])
def index():
    return "✅ ربات در حال اجراست!"

# ✳️ مسیر Webhook
@app.route(f"/bot{API_TOKEN}", methods=['POST'])
def receive_update():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

# ✳️ تنظیم Webhook (فقط یک‌بار لازم است)
@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/bot{API_TOKEN}")
    return "Webhook تنظیم شد."

# ✳️ اجرای Flask
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port)
