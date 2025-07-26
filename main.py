import telebot
from flask import Flask, request
import os
import json

API_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")  # مثل https://yourrenderurl.onrender.com/BOT_TOKEN

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

OWNER_ID = 1656900957
REQUIRED_CHANNELS = [
    '@alp_question',
    '@lostwavesea', 
    '@timestoread'
]
DATA_FILE = 'users.json'

# ----------------- 📂 Load or Create User DB --------------------
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

users = load_data()

# ----------------- ✅ Check Membership ------------------------
def is_member(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ['member', 'creator', 'administrator']:
                return False
        except Exception:
            return False
    return True

# ----------------- 🎯 Commands --------------------------
@bot.message_handler(commands=['start'])
def start(message):
    uid = str(message.from_user.id)
    if uid in users:
        bot.reply_to(message, "✅ شما قبلاً تایید شده‌اید و عضو کانال‌ها هستید.")
    else:
        markup = telebot.types.InlineKeyboardMarkup()
        for ch in REQUIRED_CHANNELS:
            markup.add(telebot.types.InlineKeyboardButton(text=f"عضویت در {ch}", url=f"https://t.me/{ch[1:]}"))
        markup.add(telebot.types.InlineKeyboardButton("✅ بررسی عضویت", callback_data="check"))
        bot.reply_to(message, "برای استفاده از ربات، لطفا در کانال‌های زیر عضو شوید:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check_membership(call):
    uid = str(call.from_user.id)
    if is_member(call.from_user.id):
        users[uid] = {"username": call.from_user.username}
        save_data(users)
        bot.edit_message_text("✅ عضویت شما تایید شد. حالا می‌تونید از ربات استفاده کنید.", call.message.chat.id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز عضو همه کانال‌ها نیستی!", show_alert=True)

# ----------------- ⚙️ مدیریت --------------------------
@bot.message_handler(commands=['panel'])
def panel(message):
    if message.from_user.id != OWNER_ID:
        return
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('👥 لیست کاربران', '📢 ارسال پیام به همه')
    bot.send_message(message.chat.id, "📌 پنل مدیریت باز شد:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "👥 لیست کاربران" and m.from_user.id == OWNER_ID)
def user_list(message):
    text = "👤 لیست کاربران ثبت شده:\n"
    for uid, info in users.items():
        text += f"• @{info.get('username', 'بدون یوزرنیم')} - {uid}\n"
    bot.send_message(message.chat.id, text or "❌ هنوز کاربری نیست.")

@bot.message_handler(func=lambda m: m.text == "📢 ارسال پیام به همه" and m.from_user.id == OWNER_ID)
def ask_broadcast(message):
    msg = bot.send_message(message.chat.id, "پیامی که میخوای به همه بفرستی رو بفرست:")
    bot.register_next_step_handler(msg, broadcast)

def broadcast(message):
    count = 0
    for uid in users:
        try:
            bot.send_message(uid, f"📢 پیام از طرف مدیر:\n\n{message.text}")
            count += 1
        except:
            continue
    bot.send_message(message.chat.id, f"✅ پیام به {count} نفر ارسال شد.")

# ----------------- 🌐 Flask Webhook --------------------------
@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'ok', 200

@app.route('/', methods=['GET'])
def index():
    return 'ربات فعال است', 200

# ----------------- 🔁 Set Webhook --------------------------
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# ----------------- 🚀 Run --------------------------
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
