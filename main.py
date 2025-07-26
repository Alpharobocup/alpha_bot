import telebot
from telebot import types
from flask import Flask, request
import os
import json

API_TOKEN = os.environ.get("BOT_TOKEN")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")
WEBHOOK_PATH = f"/bot{API_TOKEN}"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

OWNER_ID = 1656900957
COINS_PER_JOIN = 5

DATA_FILE = "data.json"
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({"users": {}, "links": []}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load_data()

default_channels = [
    {"title": "AlphaTeam", "username": "alp_question"},
    {"title": "Lost Waves", "username": "lostwavesea"},
    {"title": "Time to Read", "username": "timestoread"},
]

def edit_or_send(chat_id, text, markup=None, message_id=None):
    try:
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=["start"])
def start(message):
    uid = str(message.from_user.id)
    if uid not in data["users"]:
        data["users"][uid] = {
            "username": message.from_user.username or "ندارد",
            "coins": 0,
            "joined": False
        }
        save_data(data)
    bot.send_message(uid, "سلام! خوش آمدی به ربات تبادل اعضا.", reply_markup=main_menu())

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📢 لیست کانال‌ها", "💰 سکه‌های من", "✅ بررسی عضویت")
    markup.add("🧑‍💻 پنل مدیریت")
    return markup

@bot.message_handler(func=lambda m: m.text == "📢 لیست کانال‌ها")
def list_channels(message):
    markup = types.InlineKeyboardMarkup()
    for ch in default_channels:
        markup.add(types.InlineKeyboardButton(ch["title"], url=f"https://t.me/{ch['username']}"))
    for link in data["links"]:
        markup.add(types.InlineKeyboardButton(f"{link['first_name']} (@{link['username']})", url=f"https://t.me/{link['link'].lstrip('@')}"))
    markup.add(types.InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join"))
    bot.send_message(message.chat.id, "عضو شو و بعد بررسی عضویت رو بزن:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "💰 سکه‌های من")
def show_coins(message):
    uid = str(message.from_user.id)
    coins = data["users"].get(uid, {}).get("coins", 0)
    bot.send_message(message.chat.id, f"💰 سکه‌های شما: {coins}")

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    uid = str(call.from_user.id)
    ok = True
    for ch in default_channels:
        try:
            mem = bot.get_chat_member(f"@{ch['username']}", int(uid))
            if mem.status not in ["member", "administrator", "creator"]:
                ok = False
                break
        except:
            ok = False
            break
    for link in data["links"]:
        try:
            mem = bot.get_chat_member(link["link"], int(uid))
            if mem.status not in ["member", "administrator", "creator"]:
                ok = False
                break
        except:
            ok = False
            break

    if ok:
        if not data["users"][uid]["joined"]:
            data["users"][uid]["coins"] += COINS_PER_JOIN
            data["users"][uid]["joined"] = True
            save_data(data)
        bot.answer_callback_query(call.id, "✅ عضویت تایید شد.")
        bot.send_message(uid, f"✅ سکه جدید: {data['users'][uid]['coins']}")
    else:
        bot.answer_callback_query(call.id, "❌ عضو همه نیستی.")

@bot.message_handler(func=lambda m: m.text == "🧑‍💻 پنل مدیریت" and m.from_user.id == OWNER_ID)
def admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📥 ثبت لینک جدید", callback_data="add_link"))
    markup.add(types.InlineKeyboardButton("📢 پیام به همه", callback_data="broadcast"))
    bot.send_message(message.chat.id, "🔧 پنل مدیریت:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "add_link")
def add_link(call):
    bot.send_message(call.message.chat.id, "لینک کانال خود را ارسال کنید (با @):")
    bot.register_next_step_handler(call.message, save_link)

def save_link(message):
    if not message.text.startswith("@"):
        return bot.send_message(message.chat.id, "❌ لینک نامعتبر است.")
    data["links"].append({
        "link": message.text,
        "username": message.from_user.username or "ندارد",
        "first_name": message.from_user.first_name
    })
    save_data(data)
    bot.send_message(message.chat.id, "✅ لینک ثبت شد.")

@bot.callback_query_handler(func=lambda call: call.data == "broadcast")
def ask_broadcast(call):
    msg = bot.send_message(call.message.chat.id, "متن پیام برای همه:")
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(message):
    sent = 0
    for uid in data["users"]:
        try:
            bot.send_message(uid, f"📢 پیام مدیریت:\n\n{message.text}")
            sent += 1
        except:
            continue
    bot.send_message(message.chat.id, f"✅ پیام به {sent} نفر ارسال شد.")

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.data.decode("utf-8"))
        bot.process_new_updates([update])
        return "", 200
    return "Forbidden", 403

@app.route("/", methods=["GET"])
def index():
    return "ربات فعال است.", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + WEBHOOK_PATH )
    app.run(host="0.0.0.0", port=port)
