import telebot
from telebot import types
import os
from flask import Flask, request, abort

API_TOKEN = os.getenv("BOT_TOKEN", "7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZc0kOxo")

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

ADMIN_ID = 1656900957

CHANNELS = [
    "@alpha20288",
    "@alp_question",
    "@Alpha_Development_Team"
]

user_states = {}
user_coins = {}
user_requests = []
user_links = {}  # ذخیره لینک‌های کاربران برای تبادل
user_request_counts = {}

COINS_PER_CHANNEL = 5

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("ℹ️ اطلاعات"),
        types.KeyboardButton("📢 لیست کانال‌ها"),
        types.KeyboardButton("💰 سکه‌های من"),
        types.KeyboardButton("📞 ارتباط با مدیریت")
    )
    return markup

def contact_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("📝 ارسال پیام دلخواه"),
        types.KeyboardButton("📨 ارسال پیام آماده")
    )
    return markup

def admin_panel():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("👥 لیست درخواست‌ها"),
        types.KeyboardButton("➕ ثبت لینک جدید"),
        types.KeyboardButton("📊 تعداد عضو برای هر کاربر")
    )
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type != "private": return
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "به پنل مدیریت خوش آمدید.", reply_markup=admin_panel())
    else:
        bot.send_message(message.chat.id, "سلام! لطفاً از منوی زیر استفاده کن:", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📞 ارتباط با مدیریت")
def contact_admin(message):
    bot.send_message(message.chat.id, "یکی از گزینه‌های زیر را انتخاب کن:", reply_markup=contact_menu())

@bot.message_handler(func=lambda m: m.text == "📨 ارسال پیام آماده")
def quick_contact(message):
    user = message.from_user
    if user.username:
        user_link = f"@{user.username}"
    else:
        user_link = f"[{user.first_name}](tg://user?id={user.id})"

    user_requests.append((user.id, user_link))
    bot.send_message(ADMIN_ID, f"🔔 درخواست ارتباط از {user_link}\n\nسلام ــ تبادل", parse_mode="Markdown")
    bot.send_message(message.chat.id, "پیام شما ارسال شد.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text == "📝 ارسال پیام دلخواه")
def ask_custom_message(message):
    user_states[message.from_user.id] = "awaiting_custom_message"
    bot.send_message(message.chat.id, "پیام دلخواه خود را بنویس:")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "awaiting_custom_message")
def handle_custom_message(message):
    user_states.pop(message.from_user.id, None)
    user = message.from_user
    if user.username:
        user_link = f"@{user.username}"
    else:
        user_link = f"[{user.first_name}](tg://user?id={user.id})"

    user_requests.append((user.id, user_link))
    bot.send_message(ADMIN_ID, f"🔔 پیام جدید از {user_link}:\n\n{message.text}", parse_mode="Markdown")
    bot.send_message(message.chat.id, "پیام شما ارسال شد.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "👥 لیست درخواست‌ها")
def show_requests(message):
    if not user_requests:
        bot.send_message(ADMIN_ID, "درخواستی ثبت نشده.")
        return
    text = "📋 لیست درخواست‌ها:\n\n"
    for i, (uid, link) in enumerate(user_requests, start=1):
        text += f"{i}- {link}\n"
    bot.send_message(ADMIN_ID, text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "➕ ثبت لینک جدید")
def request_link(message):
    user_states[ADMIN_ID] = "awaiting_user_link"
    bot.send_message(ADMIN_ID, "لطفاً لینک کانال یا کاربر را وارد کنید:")

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "awaiting_user_link")
def save_user_link(message):
    user_states.pop(message.from_user.id, None)
    link = message.text.strip()
    user_links.setdefault(message.from_user.id, []).append(link)
    bot.send_message(ADMIN_ID, f"لینک ذخیره شد:\n{link}")

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and m.text == "📊 تعداد عضو برای هر کاربر")
def ask_user_id_for_members(message):
    user_states[ADMIN_ID] = "awaiting_member_count"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add("10", "50", "100", "200")
    bot.send_message(ADMIN_ID, "چه تعداد عضو به کاربر داده شود؟", reply_markup=markup)

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "awaiting_member_count")
def record_member_count(message):
    user_states.pop(message.from_user.id, None)
    count = int(message.text.strip())
    user_request_counts[message.from_user.id] = count
    bot.send_message(ADMIN_ID, f"درخواست ثبت شد: {count} عضو برای تبادل.")

# Webhook
WEBHOOK_PATH = f"/bot{API_TOKEN}"

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.data.decode("utf-8"))
        bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://alpha-bot-zkn3.onrender.com{WEBHOOK_PATH}")
    app.run(host="0.0.0.0", port=port)
