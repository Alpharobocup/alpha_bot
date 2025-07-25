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
links = []        # لینک‌های تایید شده لیست شده
user_coins = {}   # سکه‌ها {user_id: int}

COINS_PER_CHANNEL = 5

# حذف پیام قبلی و ارسال پیام جدید
def edit_or_send(chat_id, text, markup=None, message_id=None):
    try:
        if message_id:
            bot.edit_message_text(text, chat_id, message_id, reply_markup=markup, parse_mode='HTML')
        else:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')
    except Exception:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode='HTML')

# منو اصلی
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(
        types.KeyboardButton("ℹ️ اطلاعات"),
        types.KeyboardButton("📢 لیست کانال‌ها"),
        types.KeyboardButton("💰 سکه‌های من"),
        types.KeyboardButton("📞 ارتباط با مدیریت"),
        types.KeyboardButton("✅ بررسی عضویت"),
        types.KeyboardButton("📄 شرایط و قوانین")
    )
    if ADMIN_ID:
        markup.add(types.KeyboardButton("🧑‍💻 پنل مدیریت"))
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    if message.chat.type != "private": return
    user_id = message.from_user.id
    if user_id not in user_coins:
        user_coins[user_id] = 0
    bot.send_message(message.chat.id, "سلام! خوش آمدی به ربات تبادل اعضا.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True)
def menu_handler(message):
    if message.chat.type != "private": return
    text, chat_id, user_id = message.text, message.chat.id, message.from_user.id

    if text == "ℹ️ اطلاعات":
        msg = (
            "ربات تبادل اعضا به شما کمک می‌کند با عضویت در کانال‌ها سکه جمع کنید.\n"
            f"برای هر عضویت {COINS_PER_CHANNEL} سکه می‌گیرید.\nبعد از آن می‌تونید لینک ثبت کنید."
        )
        edit_or_send(chat_id, msg, main_menu(), message_id=message.message_id)

    elif text == "📄 شرایط و قوانین":
        msg = """
📜 شرایط استفاده:

1. عضویت در همه کانال‌ها الزامی است.
2. بی‌احترامی = مسدودی دائمی
3. تبلیغ بدون هماهنگی ممنوع است.
"""
        edit_or_send(chat_id, msg.strip(), main_menu(), message_id=message.message_id)

    elif text == "📢 لیست کانال‌ها":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, ch in enumerate(default_channels, 1):
            markup.add(types.InlineKeyboardButton(f"{ch['title']} (کانال {i})", url=f"https://t.me/{ch['username']}"))
        for info in links:
            markup.add(types.InlineKeyboardButton(f"{info['first_name']} (@{info['username']})", url=f"https://t.me/{info['link'].lstrip('@')}"))
        markup.add(types.InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join"))
        edit_or_send(chat_id, "روی کانال‌ها کلیک و عضو شوید، سپس روی بررسی عضویت بزنید:", markup, message_id=message.message_id)

    elif text == "💰 سکه‌های من":
        edit_or_send(chat_id, f"💰 تعداد سکه‌های شما: {user_coins.get(user_id, 0)}", main_menu(), message_id=message.message_id)

    elif text == "📞 ارتباط با مدیریت":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ارسال پیام خودکار", callback_data="auto_contact"))
        markup.add(types.InlineKeyboardButton("ارسال پیام شخصی", url=f"https://t.me/alpha_tteam"))
        edit_or_send(chat_id, "یکی از گزینه‌های ارتباط را انتخاب کنید:", markup, message_id=message.message_id)

    elif text == "✅ بررسی عضویت":
        check_join(types.SimpleNamespace(from_user=message.from_user, message=message, chat=message.chat, id=None))

    elif text == "🧑‍💻 پنل مدیریت":
        if user_id != ADMIN_ID:
            edit_or_send(chat_id, "⚠️ فقط مدیر به این بخش دسترسی دارد.", main_menu(), message_id=message.message_id)
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("📬 درخواست‌های کاربران", callback_data="show_requests"))
        markup.add(types.InlineKeyboardButton("📥 ثبت لینک جدید", callback_data="add_link"))
        edit_or_send(chat_id, "پنل مدیریت:", markup, message_id=message.message_id)

    else:
        edit_or_send(chat_id, "یکی از گزینه‌های منو را انتخاب کنید:", main_menu(), message_id=message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "auto_contact")
def auto_contact(call):
    uid, name = call.from_user.id, call.from_user.first_name
    username = call.from_user.username or "ندارد"
    bot.send_message(ADMIN_ID, f"📩 ارتباط: {name} (@{username})\n🆔 {uid}")
    bot.send_message(uid, "✅ پیام شما برای مدیریت ارسال شد.")

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    uid = call.from_user.id
    ok = True
    for ch in default_channels:
        try:
            member = bot.get_chat_member(f"@{ch['username']}", uid)
            if member.status not in ["member", "creator", "administrator"]:
                ok = False; break
        except: ok = False; break

    for info in links:
        try:
            member = bot.get_chat_member(info["link"], uid)
            if member.status not in ["member", "creator", "administrator"]:
                ok = False; break
        except: ok = False; break

    if ok:
        user_coins[uid] += COINS_PER_CHANNEL
        bot.answer_callback_query(call.id, "✅ عضویت تایید شد!")
        bot.send_message(uid, f"🎉 عضویت تایید شد.\n💰 سکه‌های جدید: {user_coins[uid]}")
    else:
        bot.answer_callback_query(call.id, "❌ عضویت کامل نیست.")
        bot.send_message(uid, "در همه کانال‌ها عضو شو و دوباره امتحان کن.")

@bot.callback_query_handler(func=lambda call: call.data == "add_link")
def add_link(call):
    bot.send_message(call.message.chat.id, "لینک کانال خود را ارسال کنید (با @):")
    bot.register_next_step_handler(call.message, receive_link)

def receive_link(message):
    if not message.text.startswith("@"): return bot.send_message(message.chat.id, "❌ لینک نامعتبر است.")
    uid = message.from_user.id
    links.append({
        "username": message.from_user.username or "ندارد",
        "first_name": message.from_user.first_name,
        "link": message.text
    })
    bot.send_message(message.chat.id, "✅ لینک ثبت شد و به لیست اضافه شد.")

@bot.callback_query_handler(func=lambda call: call.data == "show_requests")
def show_requests(call):
    if not links:
        bot.send_message(call.message.chat.id, "هیچ لینکی ثبت نشده است.")
        return
    for info in links:
        url = f"https://t.me/{info['link'].lstrip('@')}"
        bot.send_message(call.message.chat.id, f"👤 {info['first_name']} (@{info['username']})\n🔗 لینک: {url}")

WEBHOOK_PATH = f"/bot{API_TOKEN}"

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.data.decode("utf-8"))
        bot.process_new_updates([update])
        return '', 200
    else:
        return "Forbidden", 403

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://alpha-bot-zkn3.onrender.com{WEBHOOK_PATH}")
    app.run(host="0.0.0.0", port=port)
