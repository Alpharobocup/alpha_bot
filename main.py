import telebot
from telebot import types
import os
from flask import Flask, request

API_TOKEN = os.getenv("BOT_TOKEN", "7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZc0kOxo")

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

ADMIN_ID = 1656900957  # آیدی ادمین

# کانال‌ها (این لیست رو هر وقت خواستی اضافه یا کم کنی)
CHANNELS = [
    "@alpha20288",
    "@alp_question",
    "@Alpha_Development_Team"
]

user_states = {}
user_coins = {}  # ذخیره تعداد سکه‌های هر کاربر، ساده‌ترین حالت در مموری (برای ذخیره دائمی باید دیتابیس بزنی)

COINS_PER_CHANNEL = 5

# منو اصلی
def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_info = types.KeyboardButton("ℹ️ اطلاعات")
    btn_channels = types.KeyboardButton("📢 لیست کانال‌ها")
    btn_coins = types.KeyboardButton("💰 سکه‌های من")
    btn_contact = types.KeyboardButton("📞 ارتباط با مدیریت")
    markup.add(btn_info, btn_channels, btn_coins, btn_contact)
    return markup

# /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "سلام! خوش آمدی به ربات تبادل اعضا.\nلطفاً از منوی زیر استفاده کن:",
        reply_markup=main_menu()
    )

# هندل کردن دکمه‌های منو
@bot.message_handler(func=lambda m: True)
def menu_handler(message):
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

    elif text == "📢 لیست کانال‌ها":
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, username in enumerate(CHANNELS, start=1):
            url = f"https://t.me/{username.lstrip('@')}"
            markup.add(types.InlineKeyboardButton(f"کانال {i}", url=url))
        markup.add(types.InlineKeyboardButton("✅ بررسی عضویت", callback_data="check_join"))
        bot.send_message(chat_id, "لطفاً روی هر کانال کلیک کن و عضو شو، سپس روی «بررسی عضویت» بزن.", reply_markup=markup)

    elif text == "💰 سکه‌های من":
        coins = user_coins.get(user_id, 0)
        bot.send_message(chat_id, f"💰 تعداد سکه‌های شما: {coins}", reply_markup=main_menu())

        elif text == "📞 ارتباط با مدیریت":
        bot.send_message(chat_id, "در حال ارسال پیام به مدیریت...", reply_markup=main_menu())

        user_id = message.from_user.id
        first_name = message.from_user.first_name
        username = message.from_user.username

        if username:
            user_link = f"@{username}"
        else:
            user_link = f"[{first_name}](tg://user?id={user_id})"  # لینک مستقیم به پی‌وی

        # ارسال پیام به ادمین
        bot.send_message(
            ADMIN_ID,
            f"👤 کاربر {user_link} درخواست ارتباط داده:\n\nسلام ــ تبادل",
            parse_mode='Markdown'  # برای اینکه لینک کلیک‌پذیر بشه
        )

        bot.send_message(chat_id, "پیام شما به مدیریت ارسال شد. لطفاً منتظر پاسخ باشید.", reply_markup=main_menu())


    else:
        bot.send_message(chat_id, "لطفاً یکی از گزینه‌های منو را انتخاب کن.", reply_markup=main_menu())

# چک کردن عضویت
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    all_joined = True
    failed_channels = []

    coins_earned = 0

    for username in CHANNELS:
        try:
            member = bot.get_chat_member(username, user_id)
            if member.status in ['member', 'administrator', 'creator']:
                # به ازای هر کانال که عضو است سکه اضافه کن
                coins_earned += COINS_PER_CHANNEL
            else:
                all_joined = False
                failed_channels.append(username)
        except Exception:
            all_joined = False
            failed_channels.append(username)

    if all_joined:
        # اضافه کردن سکه‌ها به حساب کاربر (اینطوری مجموع حفظ میشه)
        current_coins = user_coins.get(user_id, 0)
        user_coins[user_id] = current_coins + coins_earned

        bot.answer_callback_query(call.id, "عضویت شما تایید شد و سکه اضافه شد!")
        bot.send_message(chat_id, f"✅ تبریک! شما در همه کانال‌ها عضو هستید.\n💰 {coins_earned} سکه به حساب شما اضافه شد.\nمجموع سکه‌های شما: {user_coins[user_id]}", reply_markup=main_menu())
    else:
        text = "❌ شما در این کانال‌ها عضو نیستید:\n"
        text += "\n".join([f"- {c}" for c in failed_channels])
        text += "\n\nلطفاً عضو شو و دوباره تلاش کن."
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, text, reply_markup=main_menu())

# Webhook route
WEBHOOK_PATH = f"/bot{API_TOKEN}"

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.data.decode("utf-8"))
        bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)

# Run the Flask app
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://alpha-bot-zkn3.onrender.com{WEBHOOK_PATH}")
    app.run(host="0.0.0.0", port=port)
