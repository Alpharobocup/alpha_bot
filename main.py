import telebot
from telebot import types
import os
from flask import Flask, request

API_TOKEN = os.getenv("BOT_TOKEN", "7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZc0kOxo")

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

ADMIN_ID = 1656900957  # آیدی ادمین

# کانال‌های پیش‌فرض
default_channels = [
    {"title": "AlphaTeam", "username": "alp_question"},
    {"title": "قصه امواج", "username": "lostwavesea"},
    {"title": "فلوریکا", "username": "cjjrfjrxh"},
    {"title": "time to read ( g ) ", "username": "timestoread"},
    {"title": "time to read ( c ) ", "username": "wjdxeid"},
]

# دیتای رم (حافظه) - جایگزین فایل
user_data = {}    # ذخیره درخواست‌های کاربران {user_id: {username, first_name, link}}
links = {}        # لینک‌های تایید شده {user_id: {username, first_name, link}}
user_coins = {}   # سکه‌ها {user_id: int}

COINS_PER_CHANNEL = 5

# منو اصلی
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_info = types.KeyboardButton("ℹ️ اطلاعات")
    btn_channels = types.KeyboardButton("📢 لیست کانال‌ها")
    btn_coins = types.KeyboardButton("💰 سکه‌های من")
    btn_contact = types.KeyboardButton("📞 ارتباط با مدیریت")
    btn_check = types.KeyboardButton("✅ بررسی عضویت")
    btn_rules = types.KeyboardButton("📄 شرایط و قوانین")
    btn_admin = types.KeyboardButton("🧑‍💻 پنل مدیریت")
    markup.add(btn_info, btn_channels, btn_coins, btn_contact, btn_check, btn_rules)
    if ADMIN_ID:
        markup.add(btn_admin)
    return markup

# /start
@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type != "private":
        return
    user_id = message.from_user.id
    if user_id not in user_coins:
        user_coins[user_id] = 0
    bot.send_message(
        message.chat.id,
        "سلام! خوش آمدی به ربات تبادل اعضا.\nلطفاً از منوی زیر استفاده کن:",
        reply_markup=main_menu()
    )

# هندل دکمه‌ها
@bot.message_handler(func=lambda m: True)
def menu_handler(message):
    if message.chat.type != "private":
        return
    text = message.text
    chat_id = message.chat.id
    user_id = message.from_user.id

    if text == "ℹ️ اطلاعات":
        info_text = (
            "ربات تبادل اعضا به شما کمک می‌کند با عضویت در کانال‌ها سکه جمع کنید.\n"
            f"برای هر عضویت در کانال، {COINS_PER_CHANNEL} سکه دریافت می‌کنید.\n"
            "بعد از جمع‌آوری سکه‌ها می‌توانید از خدمات تبادل استفاده کنید."
        )
        bot.send_message(chat_id, info_text, reply_markup=main_menu())

    elif text == "📄 شرایط و قوانین":
        rules = """
📜 شرایط استفاده:

1. عضویت در همه کانال‌ها الزامی است.
2. بی‌احترامی = مسدودی دائمی
3. تبلیغ بدون هماهنگی ممنوع است.
"""
        bot.send_message(chat_id, rules, reply_markup=main_menu())

    elif text == "📢 لیست کانال‌ها":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, ch in enumerate(default_channels, start=1):
            url = f"https://t.me/{ch['username']}"
            markup.add(types.InlineKeyboardButton(f"{ch['title']} (کانال {i})", url=url))
        for uid, info in links.items():
            url = f"https://t.me/{info['link'].lstrip('@')}"
            markup.add(types.InlineKeyboardButton(f"کاربر: {info['first_name']} (@{info['username']})", url=url))
        markup.add(types.InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join"))
        bot.send_message(chat_id, "لطفاً روی هر کانال کلیک کن و عضو شو، سپس روی «بررسی عضویت» بزن.", reply_markup=markup)

    elif text == "💰 سکه‌های من":
        coins = user_coins.get(user_id, 0)
        bot.send_message(chat_id, f"💰 تعداد سکه‌های شما: {coins}", reply_markup=main_menu())

    elif text == "📞 ارتباط با مدیریت":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ارسال پیام خودکار", callback_data="auto_contact"))
        markup.add(types.InlineKeyboardButton("ارسال پیام شخصی", url=f"https://t.me/user?id={ADMIN_ID}"))
        bot.send_message(chat_id, "یکی از گزینه‌های ارتباط را انتخاب کنید:", reply_markup=markup)

    elif text == "✅ بررسی عضویت":
        check_join(types.SimpleNamespace(from_user=message.from_user, message=message, chat=message.chat, id=None))

    elif text == "🧑‍💻 پنل مدیریت":
        if message.from_user.id != ADMIN_ID:
            bot.send_message(chat_id, "⚠️ دسترسی فقط برای مدیریت است.")
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📬 درخواست‌های کاربران", callback_data="show_requests"))
        markup.add(types.InlineKeyboardButton("📥 ثبت لینک جدید", callback_data="add_link"))
        bot.send_message(chat_id, "پنل مدیریت:", reply_markup=markup)

    else:
        bot.send_message(chat_id, "لطفاً یکی از گزینه‌های منو را انتخاب کن.", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data == "auto_contact")
def auto_contact(call):
    uid = call.from_user.id
    first_name = call.from_user.first_name
    username = call.from_user.username or "ندارد"
    bot.send_message(ADMIN_ID, f"📩 درخواست ارتباط:👤 {first_name} (@{username})\n🆔 {uid}")
    bot.send_message(uid, "✅ پیام شما برای مدیریت ارسال شد.")

# باقی کدها (مثل قبل) بدون تغییر باقی می‌مونه...

# webhook
WEBHOOK_PATH = f"/bot{API_TOKEN}"

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.data.decode("utf-8"))
        bot.process_new_updates([update])
        return '', 200
    else:
        return "Forbidden", 403
# بررسی عضویت
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    user_id = call.from_user.id
    status_ok = True
    for ch in default_channels:
        try:
            member = bot.get_chat_member(f"@{ch['username']}", user_id)
            if member.status not in ["member", "creator", "administrator"]:
                status_ok = False
                break
        except Exception:
            status_ok = False
            break

    for uid, info in links.items():
        try:
            member = bot.get_chat_member(info["link"], user_id)
            if member.status not in ["member", "creator", "administrator"]:
                status_ok = False
                break
        except Exception:
            status_ok = False
            break

    if status_ok:
        user_coins[user_id] += COINS_PER_CHANNEL
        bot.answer_callback_query(call.id, "✅ عضویت تایید شد! سکه اضافه شد.")
        bot.send_message(user_id, f"🎉 عضویت شما تایید شد.\n💰 سکه‌های جدید شما: {user_coins[user_id]}")
    else:
        bot.answer_callback_query(call.id, "❌ عضویت کامل نیست.")
        bot.send_message(user_id, "لطفاً در همه کانال‌ها عضو شوید و دوباره امتحان کنید.")

# ثبت لینک جدید
@bot.callback_query_handler(func=lambda call: call.data == "add_link")
def add_link(call):
    bot.send_message(call.message.chat.id, "لینک کانال خود را بفرستید (با @ شروع شود):")
    bot.register_next_step_handler(call.message, receive_link)

def receive_link(message):
    if not message.text.startswith("@"):
        bot.send_message(message.chat.id, "❌ لینک نامعتبر است. لطفاً با @ شروع شود.")
        return
    user_id = message.from_user.id
    username = message.from_user.username or "ندارد"
    first_name = message.from_user.first_name
    links[user_id] = {
        "username": username,
        "first_name": first_name,
        "link": message.text
    }
    bot.send_message(message.chat.id, "✅ لینک با موفقیت ثبت شد و به لیست کانال‌ها اضافه شد.")

# نمایش درخواست‌ها
@bot.callback_query_handler(func=lambda call: call.data == "show_requests")
def show_requests(call):
    if not links:
        bot.send_message(call.message.chat.id, "هیچ لینکی ثبت نشده است.")
        return
    for uid, info in links.items():
        link_url = f"https://t.me/{info['link'].lstrip('@')}"
        bot.send_message(
            call.message.chat.id,
            f"👤 {info['first_name']} (@{info['username']})\n🆔 {uid}\n🔗 لینک: {link_url}"
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://alpha-bot-zkn3.onrender.com{WEBHOOK_PATH}")
    app.run(host="0.0.0.0", port=port)
