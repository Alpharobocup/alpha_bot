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
    #{"title": "Time to Read (C)", "username": "timestoread"},
    {"title": "Time to Read (G) ", "username": "timestoreads"},
    {"title": "Alpha(support)", "username": "Alpha_Development_Team"},
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
    bot.send_message(uid, "سلام! به ربات تبادل اعضا خوش اومدی .", reply_markup=main_menu())

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📢 لیست کانال‌ها", "💰 سکه‌های من", "✅ بررسی عضویت")
    markup.add("","📄 شرایط و قوانین","ℹ️ اطلاعات"   , "📞 ارتباط با ادمین")
    markup.add("🧑‍💻 پنل ادمین")
    return markup
    
@bot.message_handler(func=lambda m: m.text == "ℹ️ اطلاعات")  
def information_(message):
    uid = str(message.from_user.id)
    msg = (
        "ربات تبادل اعضا به شما کمک می‌کند با عضویت در کانال‌ها سکه جمع کنید.\n"
        f"برای هر سری عضویت {COINS_PER_JOIN} سکه می‌گیرید.\nبعد از آن می‌تونید لینک ثبت کنید."
    )
    bot.send_message(uid , msg )
    #edit_or_send(message.chat.id, msg, main_menu(), message_id=message.message_id)

@bot.message_handler(func=lambda m: m.text == "📄 شرایط و قوانین")
def rules_(message):
    uid = str(message.from_user.id)
    msg = """
    📜 شرایط استفاده:
     
     1. عضویت در همه کانال‌ها الزامی است.
     2. بی‌احترامی = مسدودی دائمی
     3. تبلیغ بدون هماهنگی ممنوع است.
    """
    bot.send_message(uid , msg )
    #edit_or_send(message.chat.id, msg.strip(), main_menu(), message_id=message.message_id)
@bot.message_handler(func=lambda m: m.text == "✅ بررسی عضویت")
def check_dokme(call):
    uid = str(call.from_user.id)
    user = data["users"].get(uid, {})
    if not user:
        return bot.answer_callback_query(call.id, "❌ کاربر ناشناس.")

    all_channels = default_channels + data.get("links", [])
    all_ok = True
    for ch in all_channels:
        username = ch["username"] if "username" in ch else ch["link"].lstrip("@")
        if not is_member(username, int(uid)):
            all_ok = False
            break

    if all_ok:
        if not user.get("joined", False):
            user["joined"] = True
            user["coins"] += COINS_PER_JOIN
            data["users"][uid] = user
            save_data(data)
            bot.answer_callback_query(call.id, "✅ عضویت تایید شد و سکه دریافت شد." )
        else:
            bot.answer_callback_query(call.id, "✅ قبلاً عضو شدی.")
        bot.send_message(uid, f"💰 سکه فعلی: {user['coins']}")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📥 ثبت لینک", callback_data="add_link_user"))
    bot.send_message(message.chat.id, "روی ثبت لینک کلیک کن تا لینک ارسالی برای ادمین ارسال بشه ", reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز در همه کانال‌ها عضو نیستید.")


@bot.message_handler(func=lambda m: m.text == "📞 ارتباط با ادمین")
def admins_conect(message):
    uid = str(message.from_user.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ارسال پیام خودکار", callback_data="auto_contact"))
    markup.add(types.InlineKeyboardButton("ارسال پیام شخصی", url=f"https://t.me/alpha_tteam"))
    bot.send_message(message.chat.id, "یکی از گزینه‌های ارتباط رو انتخاب کن:", reply_markup=markup)

    

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

def is_member(channel_username, user_id):
    try:
        member = bot.get_chat_member(f"@{channel_username}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    uid = str(call.from_user.id)
    user = data["users"].get(uid, {})
    if not user:
        return bot.answer_callback_query(call.id, "❌ کاربر ناشناس.")

    all_channels = default_channels + data.get("links", [])
    all_ok = True
    for ch in all_channels:
        username = ch["username"] if "username" in ch else ch["link"].lstrip("@")
        if not is_member(username, int(uid)):
            all_ok = False
            break

    if all_ok:
        if not user.get("joined", False):
            user["joined"] = True
            user["coins"] += COINS_PER_JOIN
            data["users"][uid] = user
            save_data(data)
            bot.answer_callback_query(call.id, "✅ عضویت تایید شد و سکه دریافت شد." )
        else:
            bot.answer_callback_query(call.id, "✅ قبلاً عضو شدی.")
        bot.send_message(uid, f"💰 سکه فعلی: {user['coins']}")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📥 ثبت لینک", callback_data="add_link_user"))
    bot.send_message(message.chat.id, "روی ثبت لینک کلیک کن تا لینک ارسالی برای ادمین ارسال بشه ", reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "❌ هنوز در همه کانال‌ها عضو نیستی.")



@bot.message_handler(func=lambda m: m.text == "🧑‍💻 پنل ادمین" and m.from_user.id == OWNER_ID)
def admin_panel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📥 ثبت لینک جدید", callback_data="add_link"))
    markup.add(types.InlineKeyboardButton("📢 پیام به همه", callback_data="broadcast"))
    markup.add(types.InlineKeyboardButton("👥 لیست کاربران", callback_data="list_karbar"))
    bot.send_message(message.chat.id, "🔧 پنل ادمین:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "auto_contact")
def auto_contact(call):
    uid, name = call.from_user.id, call.from_user.first_name
    username = call.from_user.username or "ندارد"
    bot.send_message(OWNER_ID, f"📩 ارتباط: {name} (@{username})\n🆔 {uid}")
    bot.send_message(call.id, "✅ پیام شما برای ادمین فرستاده شد.")
   
@bot.callback_query_handler(func=lambda call: call.data == "list_karbar")
def user_list(call):
    if call.from_user.id != OWNER_ID:
        return bot.answer_callback_query(call.id, "⛔️ دسترسی نداری.")
    text = "👤 لیست کاربران:\n"
    for uid, info in data["users"].items():
        username = info.get("username", "ندارد")
        text += f"• @{username} - {uid}\n"
    bot.send_message(call.message.chat.id, text or "❌ کاربری ثبت نشده.")

@bot.callback_query_handler(func=lambda call: call.data == "add_link_user")
def add_link_user(call):
    uid = call.from_user.id
    bot.send_message(call.message.chat.id, "آیدی کانال یا گروهت رو بفرست (با @):")
    bot.send_message(OWNER_ID, f"📩 link: { call.message } \n {name} (@{username})\n🆔 {uid}")
    #bot.register_next_step_handler(call.message, save_link)

@bot.callback_query_handler(func=lambda call: call.data == "add_link")
def add_link(call):
    bot.send_message(call.message.chat.id, "لینک کانال درخواستی رو بفرست (با @):")
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
            bot.send_message(uid, f"📢 پیام ادمین:\n\n{message.text}")
            sent += 1
        except:
            continue
    bot.send_message(message.chat.id, f"✅ پیام به {sent} نفر فرستاده شد.")

@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(request.data.decode("utf-8"))
        bot.process_new_updates([update])
        return "", 200
    return "Forbidden", 403

@app.route("/", methods=["GET"])
def index():
    return "ربات فعال.", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL + WEBHOOK_PATH )
    app.run(host="0.0.0.0", port=port)
