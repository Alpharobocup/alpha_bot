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
    {"title": "AlphaTeam", "username": "AlphaRoboCup"},
    {"title": "NewsBot", "username": "TechNewsAlpha"},
    {"title": "CodeZone", "username": "AlphaCodeTeam"}
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
    
    btn_admin = types.KeyboardButton("🧑‍💻 پنل مدیریت")
    if ADMIN_ID:
        markup.add(btn_info, btn_channels, btn_coins, btn_contact, btn_admin)
    else:
        markup.add(btn_info, btn_channels, btn_coins, btn_contact)
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

    elif text == "📢 لیست کانال‌ها":
        markup = types.InlineKeyboardMarkup(row_width=1)
        # کانال‌های پیش‌فرض
        for i, ch in enumerate(default_channels, start=1):
            url = f"https://t.me/{ch['username']}"
            markup.add(types.InlineKeyboardButton(f"{ch['title']} (کانال {i})", url=url))
        # کانال‌های ثبت شده توسط مدیر
        for uid, info in links.items():
            url = f"https://t.me/{info['link'].lstrip('@')}"
            markup.add(types.InlineKeyboardButton(f"کاربر: {info['first_name']} (@{info['username']})", url=url))
        bot.send_message(chat_id, "لطفاً روی هر کانال کلیک کن و عضو شو، سپس روی «بررسی عضویت» بزن.", reply_markup=markup)

    elif text == "💰 سکه‌های من":
        coins = user_coins.get(user_id, 0)
        bot.send_message(chat_id, f"💰 تعداد سکه‌های شما: {coins}", reply_markup=main_menu())
        
    elif text == "📞 ارتباط با مدیریت":
        bot.send_message(chat_id, "در حال ارسال پیام به مدیریت...", reply_markup=main_menu())

        first_name = message.from_user.first_name
        username = message.from_user.username

        if username:
            user_link = f"@{username}"
        else:
            user_link = f"(tg://user?id={user_id})"  # لینک مستقیم به پی‌وی

        # ذخیره درخواست کاربر
        user_data[user_id] = {
            "username": username or "ندارد",
            "first_name": first_name,
            "link": None  # کاربر میتونه بعدا لینک ارسال کنه اگر خواست
        }

        # ارسال پیام به ادمین
        bot.send_message(
            ADMIN_ID,
            f"👤 کاربر {user_link} درخواست ارتباط داده:\n\nسلام ــ تبادل",
            parse_mode='Markdown'
        )

        bot.send_message(chat_id, "پیام شما به مدیریت ارسال شد. لطفاً منتظر پاسخ باشید.", reply_markup=main_menu())

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

# دریافت لینک کاربر بعد از درخواست ارتباط (اختیاری)
@bot.message_handler(func=lambda m: m.chat.type == "private" and user_data.get(m.from_user.id, {}).get("link") is None)
def receive_user_link(message):
    user_id = message.from_user.id
    if user_id not in user_data:
        return
    user_data[user_id]['link'] = message.text
    bot.send_message(message.chat.id, "لینک شما ثبت شد و در انتظار تایید مدیر است.", reply_markup=main_menu())

    # اطلاع مدیر
    first_name = user_data[user_id]['first_name']
    username = user_data[user_id]['username']
    link = user_data[user_id]['link']
    bot.send_message(ADMIN_ID, f"🔔 درخواست جدید ثبت لینک:\n👤 {first_name} (@{username})\n🔗 {link}",
                     reply_markup=types.InlineKeyboardMarkup().add(
                         types.InlineKeyboardButton("ثبت در لیست", callback_data=f"confirm_{user_id}")
                     ))

# نمایش درخواست‌های ثبت لینک به مدیر
@bot.callback_query_handler(func=lambda call: call.data == "show_requests")
def show_requests(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "دسترسی ندارید.")
        return
    if not user_data:
        bot.send_message(call.message.chat.id, "درخواستی ثبت نشده.")
        return
    for uid, info in user_data.items():
        if info.get("link"):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("ثبت لینک در کانال‌ها", callback_data=f"confirm_{uid}"))
            text = f"👤 {info['first_name']} (@{info['username']})\n🔗 {info['link']}\n🆔 {uid}"
            bot.send_message(call.message.chat.id, text, reply_markup=markup)

# تایید و ثبت لینک توسط مدیر
@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_link(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "دسترسی ندارید.")
        return
    uid = int(call.data.split("_")[1])
    if uid not in user_data:
        bot.answer_callback_query(call.id, "کاربر یافت نشد.")
        return
    links[uid] = user_data[uid]
    bot.answer_callback_query(call.id, "لینک ثبت شد.")
    bot.send_message(ADMIN_ID, f"✅ لینک کاربر {user_data[uid]['first_name']} ثبت شد.")
    bot.send_message(uid, "✅ لینک شما توسط مدیر تایید و ثبت شد.")

# ثبت لینک جدید توسط مدیر
@bot.callback_query_handler(func=lambda call: call.data == "add_link")
def add_link_start(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "دسترسی ندارید.")
        return
    msg = bot.send_message(call.message.chat.id, "لطفاً لینک جدید را وارد کنید:")
    bot.register_next_step_handler(msg, add_link_save)

def add_link_save(message):
    if message.from_user.id != ADMIN_ID:
        return
    # فرض میکنیم لینک به صورت کامل یا فقط یوزرنیم هست
    new_link = message.text.strip()
    # ذخیره به عنوان یک لینک جدید با user_id = -1 (برای کانال عمومی)
    links[-1] = {
        "username": "",
        "first_name": "کانال جدید",
        "link": new_link
    }
    bot.send_message(message.chat.id, f"✅ لینک {new_link} به لیست کانال‌ها اضافه شد.")

# چک کردن عضویت (مانند قبلی)
@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def check_join(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    all_joined = True
    failed_channels = []

    coins_earned = 0

    # کانال‌ها = پیش‌فرض + لینک‌های ثبت شده
    all_channels = default_channels.copy()
    # اضافه کردن لینک‌های تایید شده که user_id != -1
    for uid, info in links.items():
        if uid != -1:
            all_channels.append({"title": info['first_name'], "username": info['link']})

    for ch in all_channels:
        try:
            member = bot.get_chat_member(ch["username"], user_id)
            if member.status in ['member', 'administrator', 'creator']:
                coins_earned += COINS_PER_CHANNEL
            else:
                all_joined = False
                failed_channels.append(ch["username"])
        except Exception:
            all_joined = False
            failed_channels.append(ch["username"])

    if all_joined:
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://alpha-bot-zkn3.onrender.com{WEBHOOK_PATH}")
    app.run(host="0.0.0.0", port=port)
