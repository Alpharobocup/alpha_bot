import telebot
from telebot import types
from flask import Flask, request
import json
import os
import threading
import requests
from datetime import datetime, timedelta

TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
bot = telebot.TeleBot(TOKEN, parse_mode='HTML')

group_settings = {}

# ذخیره تنظیمات در فایل json
def save_settings():
    with open("group_settings.json", "w") as f:
        json.dump(group_settings, f)

# بارگذاری تنظیمات
def load_settings():
    global group_settings
    if os.path.exists("group_settings.json"):
        with open("group_settings.json", "r") as f:
            group_settings = json.load(f)

load_settings()

# بررسی مالک
def get_owner(chat_id):
    return group_settings.get(str(chat_id), {}).get("owner", None)

# تنظیم مالک
@bot.message_handler(commands=["set_owner"])
def set_owner(msg):
    chat_id = msg.chat.id
    if msg.chat.type != "supergroup":
        return bot.reply_to(msg, "این دستور فقط داخل سوپرگروه کار می‌کنه.")
    user_id = msg.from_user.id
    group_settings[str(chat_id)] = group_settings.get(str(chat_id), {})
    group_settings[str(chat_id)]["owner"] = user_id
    save_settings()
    bot.reply_to(msg, "✅ شما به‌عنوان مالک گروه ذخیره شدید.")

# پیام خوش‌آمد
@bot.message_handler(content_types=["new_chat_members"])
def welcome(msg):
    name_list = [m.first_name for m in msg.new_chat_members]
    bot.send_message(msg.chat.id, f"🎉 خوش‌اومدید {'، '.join(name_list)}")

# حذف پیام ورود و خروج
@bot.message_handler(content_types=["left_chat_member"])
def left(msg):
    try:
        bot.delete_message(msg.chat.id, msg.message_id)
    except:
        pass

@bot.message_handler(func=lambda m: m.text and "joined" in m.text.lower())
def joined(msg):
    try:
        bot.delete_message(msg.chat.id, msg.message_id)
    except:
        pass

# حذف کاربر با ریپلای
@bot.message_handler(func=lambda msg: msg.reply_to_message and msg.text.lower() == "حذف")
def delete_user(msg):
    admins = bot.get_chat_administrators(msg.chat.id)
    if msg.from_user.id in [a.user.id for a in admins]:
        try:
            bot.ban_chat_member(msg.chat.id, msg.reply_to_message.from_user.id)
            bot.unban_chat_member(msg.chat.id, msg.reply_to_message.from_user.id)
            bot.send_message(msg.chat.id, "✅ کاربر حذف شد.")
        except:
            bot.send_message(msg.chat.id, "⛔️ نتونستم حذفش کنم.")

# سکوت عددی
@bot.message_handler(func=lambda msg: msg.text.lower().startswith("سکوت "))
def mute_user(msg):
    if not msg.reply_to_message:
        return
    try:
        admins = bot.get_chat_administrators(msg.chat.id)
        if msg.from_user.id in [a.user.id for a in admins]:
            duration = int(msg.text.split()[1])
            until = datetime.now() + timedelta(minutes=duration)
            bot.restrict_chat_member(
                msg.chat.id,
                msg.reply_to_message.from_user.id,
                until_date=until,
                can_send_messages=False
            )
            bot.reply_to(msg, f"🔇 کاربر به مدت {duration} دقیقه در سکوت قرار گرفت.")
    except:
        bot.send_message(msg.chat.id, "⛔️ مشکلی پیش اومد.")

# /start پیام اولیه با دکمه افزودن
@bot.message_handler(commands=["start"])
def start(msg):
    markup = types.InlineKeyboardMarkup()
    add_btn = types.InlineKeyboardButton("➕ افزودن به گروه", url=f"https://t.me/YourBotUsername?startgroup=true")
    markup.add(add_btn)
    bot.send_message(msg.chat.id, "🤖 سلام! من ربات گروه شما هستم. لطفاً منو تو گروه ادمین کنید.", reply_markup=markup)

# /be_zoodi فقط در پی‌وی فعال
@bot.message_handler(commands=["be_zoodi"])
def be_zoodi(msg):
    if msg.chat.type == 'private':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📅 تقویم امروز", "🕋 اوقات شرعی", "📜 شعر", "😂 جوک")
        bot.send_message(msg.chat.id, "💡 انتخاب کنید:", reply_markup=markup)
    else:
        bot.send_message(msg.chat.id, "📩 این دستور فقط در پی‌وی فعال است:\n👉 @YourBotUsername")

# پاسخ به دکمه‌های منو
@bot.message_handler(func=lambda msg: msg.text in ["📅 تقویم امروز", "🕋 اوقات شرعی", "📜 شعر", "😂 جوک"])
def handle_buttons(msg):
    if msg.text == "📅 تقویم امروز":
        bot.reply_to(msg, "📅 امروز " + datetime.now().strftime("%Y/%m/%d"))
    elif msg.text == "🕋 اوقات شرعی":
        bot.reply_to(msg, "🕋 فعلاً اوقات شرعی فعال نیست.")
    elif msg.text == "📜 شعر":
        bot.reply_to(msg, "🍂 زندگی چیست؟ نگاه خسته‌ای بر پنجره.")
    elif msg.text == "😂 جوک":
        bot.reply_to(msg, "😂 چرا کامپیوتر نخندید؟ چون بایت نداشت!")

# جستجوی گوگل
@bot.message_handler(commands=["google"])
def google_search(msg):
    q = msg.text.split(" ", 1)
    if len(q) < 2:
        return bot.reply_to(msg, "❓ لطفاً عبارتی برای جستجو وارد کنید.")
    query = q[1]
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    bot.send_message(msg.chat.id, f"🔍 نتیجه:\n{url}")

# تنظیم پیام‌های زمان‌دار (مثلاً صبح بخیر)
def send_scheduled_messages():
    while True:
        now = datetime.now().strftime("%H:%M")
        for chat_id, data in group_settings.items():
            owner = data.get("owner")
            if not owner:
                continue
            if data.get("morning") == now:
                bot.send_message(chat_id, "☀️ صبح بخیر دوستای عزیز!")
            if data.get("night") == now:
                bot.send_message(chat_id, "🌙 شب بخیر دوستان 🌙")
        time.sleep(60)

# webhook flask app
app = Flask(__name__)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'OK', 200

@app.route("/", methods=['GET'])
def index():
    return "💡 ربات آنلاین است!"

def run():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

# تنظیم وب‌هوک
bot.remove_webhook()
bot.set_webhook(url=f"https://alpha-bot-zkn3.onrender.com/{TOKEN}")

# اجرای Flask
threading.Thread(target=run).start()
