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

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇮🇷 فارسی", "🇬🇧 English")
    bot.send_message(message.chat.id, "لطفاً زبان را انتخاب کنید:\nPlease select your language:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text in ["🇮🇷 فارسی", "🇬🇧 English"])
def set_language(message):
    uid = str(message.from_user.id)
    lang = "fa" if message.text == "🇮🇷 فارسی" else "en"
    data["users"][uid]["language"] = lang
    save_data(data)

    if lang == "fa":
        bot.send_message(message.chat.id, "سلام! به ربات تبادل اعضا خوش اومدی.", reply_markup=main_menu("fa"))
    else:
        bot.send_message(message.chat.id, "Hi! Welcome to the member exchange bot.", reply_markup=main_menu("en"))


def main_menu(lang="fa"):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "fa":
        markup.add("📢 لیست کانال‌ها", "💰 سکه‌های من", "✅ بررسی عضویت")
        markup.add("📄 شرایط و قوانین", "ℹ️ اطلاعات", "📞 ارتباط با ادمین")
        markup.add("🧑‍💻 پنل ادمین")
    else:
        markup.add("📢 Channel List", "💰 My Coins", "✅ Check Join")
        markup.add("📄 Terms & Rules", "ℹ️ Info", "📞 Contact Admin")
        markup.add("🧑‍💻 Admin Panel")
    return markup


@bot.message_handler(func=lambda m: m.text in ["ℹ️ اطلاعات", "ℹ️ Info"])
def information_(message):
    uid = str(message.from_user.id)
    lang = data["users"].get(uid, {}).get("language", "fa")
    if lang == "fa":
        msg = (
            "ربات تبادل اعضا به شما کمک می‌کند با عضویت در کانال‌ها سکه جمع کنید.\n"
            f"برای هر سری عضویت {COINS_PER_JOIN} سکه می‌گیرید.\nبعد از آن می‌تونید لینک ثبت کنید."
        )
    else:
        msg = (
            "This bot helps you collect coins by joining channels.\n"
            f"You get {COINS_PER_JOIN} coins per join.\nThen you can submit your channel link."
        )
    bot.send_message(message.chat.id, msg)


@bot.message_handler(func=lambda m: m.text in ["📄 شرایط و قوانین", "📄 Terms & Rules"])
def rules_(message):
    uid = str(message.from_user.id)
    lang = data["users"].get(uid, {}).get("language", "fa")
    if lang == "fa":
        msg = """
    📜 شرایط استفاده:
     1. عضویت در همه کانال‌ها الزامی است.
     2. بی‌احترامی = مسدودی دائمی
     3. تبلیغ بدون هماهنگی ممنوع است.
        """
    else:
        msg = """
    📜 Terms of Use:
     1. You must join all channels.
     2. Disrespect = Permanent ban
     3. Advertising without permission is prohibited.
        """
    bot.send_message(message.chat.id, msg.strip())


@bot.message_handler(func=lambda m: m.text in ["📞 ارتباط با ادمین", "📞 Contact Admin"])
def admins_conect(message):
    uid = str(message.from_user.id)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("ارسال پیام خودکار / Auto Send", callback_data="auto_contact"))
    markup.add(types.InlineKeyboardButton("ارسال پیام شخصی / Personal Message", url=f"https://t.me/alpha_tteam"))
    bot.send_message(message.chat.id, "یکی از گزینه‌های ارتباط رو انتخاب کن:\nChoose one of the contact options:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text in ["📢 لیست کانال‌ها", "📢 Channel List"])
def list_channels(message):
    markup = types.InlineKeyboardMarkup()
    for ch in default_channels:
        markup.add(types.InlineKeyboardButton(ch["title"], url=f"https://t.me/{ch['username']}"))
    for link in data["links"]:
        markup.add(types.InlineKeyboardButton(f"{link['first_name']} (@{link['username']})", url=f"https://t.me/{link['link'].lstrip('@')}"))
    markup.add(types.InlineKeyboardButton("✅ بررسی عضویت / Check Join", callback_data="check_join"))
    bot.send_message(message.chat.id, "عضو شو و بعد بررسی عضویت رو بزن:\nJoin all channels and then click check:", reply_markup=markup)


@bot.message_handler(func=lambda m: m.text in ["💰 سکه‌های من", "💰 My Coins"])
def show_coins(message):
    uid = str(message.from_user.id)
    coins = data["users"].get(uid, {}).get("coins", 0)
    lang = data["users"].get(uid, {}).get("language", "fa")
    if lang == "fa":
        bot.send_message(message.chat.id, f"💰 سکه‌های شما: {coins}")
    else:
        bot.send_message(message.chat.id, f"💰 Your coins: {coins}")

def is_member(channel_username, user_id):
    try:
        member = bot.get_chat_member(f"@{channel_username}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    markup = types.InlineKeyboardMarkup()
    uid = str(call.from_user.id)
    user = data["users"].get(uid, {})
    lang = user_language.get(call.from_user.id, "fa")

    if not user:
        text1 = "❌ Unknown user."
        text2 = "⛔️ Please send /start to register."
        if lang == "fa":
            text1 = "❌ کاربر ناشناس."
            text2 = "⛔️ ابتدا /start را بزنید تا ثبت شوید."
        bot.answer_callback_query(call.id, text1)
        bot.send_message(call.message.chat.id, text2)
        return

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
            text = "✅ Membership confirmed and coins awarded."
            if lang == "fa":
                text = "✅ عضویت تایید شد و سکه دریافت شد."
            bot.answer_callback_query(call.id, text)
        else:
            text = "✅ You already joined."
            if lang == "fa":
                text = "✅ قبلاً عضو شدی."
            bot.answer_callback_query(call.id, text)
        
        coins_msg = f"💰 Current coins: {user['coins']}" if lang == "en" else f"💰 سکه فعلی: {user['coins']}"
        bot.send_message(call.message.chat.id, coins_msg)
        btn_text = "📥 Submit Link" if lang == "en" else "📥 ثبت لینک"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data="add_link_user"))
        link_msg = "Click Submit Link to send your link to admin." if lang == "en" else "روی ثبت لینک کلیک کن تا لینک ارسالی برای ادمین ارسال بشه"
        bot.send_message(call.message.chat.id, link_msg, reply_markup=markup)
    else:
        text = "❌ You are not a member of all channels yet."
        if lang == "fa":
            text = "❌ هنوز در همه کانال‌ها عضو نیستی."
        bot.answer_callback_query(call.id, text)


@bot.message_handler(func=lambda m: m.text in ["🧑‍💻 Admin Panel", "🧑‍💻 پنل ادمین"] and m.from_user.id == OWNER_ID)
def admin_panel(message):
    lang = user_language.get(message.from_user.id, "fa")
    markup = types.InlineKeyboardMarkup()
    btn_add_link = "📥 Add New Link" if lang == "en" else "📥 ثبت لینک جدید"
    btn_broadcast = "📢 Broadcast Message" if lang == "en" else "📢 پیام به همه"
    btn_user_list = "👥 User List" if lang == "en" else "👥 لیست کاربران"
    markup.add(types.InlineKeyboardButton(btn_add_link, callback_data="add_link"))
    markup.add(types.InlineKeyboardButton(btn_broadcast, callback_data="broadcast"))
    markup.add(types.InlineKeyboardButton(btn_user_list, callback_data="list_karbar"))
    panel_text = "🔧 Admin Panel:" if lang == "en" else "🔧 پنل ادمین:"
    bot.send_message(message.chat.id, panel_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "auto_contact")
def auto_contact(call):
    uid, name = call.from_user.id, call.from_user.first_name
    username = call.from_user.username or "ندارد"
    bot.send_message(OWNER_ID, f"📩 Contact: {name} (@{username})\n🆔 {uid}")
    lang = user_language.get(call.from_user.id, "fa")
    confirm_msg = "✅ Your message was sent to admin." if lang == "en" else "✅ پیام شما برای ادمین فرستاده شد."
    bot.send_message(call.id, confirm_msg)
   
@bot.callback_query_handler(func=lambda call: call.data == "list_karbar")
def user_list(call):
    if call.from_user.id != OWNER_ID:
        lang = user_language.get(call.from_user.id, "fa")
        no_access = "⛔️ You don't have access." if lang == "en" else "⛔️ دسترسی نداری."
        return bot.answer_callback_query(call.id, no_access)
    text = "👤 User List:\n" if user_language.get(call.from_user.id, "fa") == "en" else "👤 لیست کاربران:\n"
    for uid, info in data["users"].items():
        username = info.get("username", "ندارد")
        text += f"• @{username} - {uid}\n"
    no_user_text = "❌ No registered users." if user_language.get(call.from_user.id, "fa") == "en" else "❌ کاربری ثبت نشده."
    bot.send_message(call.message.chat.id, text or no_user_text)

@bot.callback_query_handler(func=lambda call: call.data == "add_link_user")
def add_link_user(call):
    lang = user_language.get(call.from_user.id, "fa")
    prompt = "✅ Send your channel or group ID (with @):" if lang == "en" else "✅ آیدی کانال یا گروهت رو بفرست (با @):"
    bot.send_message(call.message.chat.id, prompt)
    
    bot.register_next_step_handler(call.message, forward_link_to_admin, call.from_user.id)


def forward_link_to_admin(message, uid):
    try:
        username = message.from_user.username or "ندارد"
        name = message.from_user.first_name
        bot.forward_message(OWNER_ID, message.chat.id, message.message_id)
        bot.send_message(OWNER_ID, f"👤 From {name} (@{username})\n🆔 {uid}")
        lang = user_language.get(message.from_user.id, "fa")
        confirm = "✅ Your link was sent to the admin." if lang == "en" else "✅ لینک شما برای مدیریت ارسال شد."
        bot.send_message(message.chat.id, confirm)
    except Exception as e:
        lang = user_language.get(message.from_user.id, "fa")
        error_msg = "❌ There was an error sending the link." if lang == "en" else "❌ مشکلی در ارسال لینک پیش آمد."
        bot.send_message(message.chat.id, error_msg)
        print(f"Error forwarding link: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "add_link")
def add_link(call):
    lang = user_language.get(call.from_user.id, "fa")
    prompt = "Send the requested channel link (with @):" if lang == "en" else "لینک کانال درخواستی رو بفرست (با @):"
    bot.send_message(call.message.chat.id, prompt)
    bot.register_next_step_handler(call.message, save_link)

def save_link(message):
    if not message.text.startswith("@"):
        lang = user_language.get(message.from_user.id, "fa")
        invalid_msg = "❌ Invalid link." if lang == "en" else "❌ لینک نامعتبر است."
        return bot.send_message(message.chat.id, invalid_msg)
    data["links"].append({
        "link": message.text,
        "username": message.from_user.username or "ندارد",
        "first_name": message.from_user.first_name
    })
    save_data(data)
    lang = user_language.get(message.from_user.id, "fa")
    saved_msg = "✅ Link saved." if lang == "en" else "✅ لینک ثبت شد."
    bot.send_message(message.chat.id, saved_msg)

@bot.callback_query_handler(func=lambda call: call.data == "broadcast")
def ask_broadcast(call):
    lang = user_language.get(call.from_user.id, "fa")
    prompt = "Message text for everyone:" if lang == "en" else "متن پیام برای همه:"
    msg = bot.send_message(call.message.chat.id, prompt)
    bot.register_next_step_handler(msg, do_broadcast)

def do_broadcast(message):
    sent = 0
    for uid in data["users"]:
        try:
            lang = user_language.get(int(uid), "fa")
            admin_msg = f"📢 Admin message:\n\n{message.text}" if lang == "en" else f"📢 پیام ادمین:\n\n{message.text}"
            bot.send_message(uid, admin_msg)
            sent += 1
        except:
            continue
    lang = user_language.get(message.from_user.id, "fa")
    done_msg = f"✅ Message sent to {sent} users." if lang == "en" else f"✅ پیام به {sent} نفر فرستاده شد."
    bot.send_message(message.chat.id, done_msg)


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
