import telebot
from telebot import types
import datetime
import requests
import os
from flask import Flask, request

API_TOKEN = 'bot7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
OWNER_ID = 1656900957  # آی‌دی عددی تو
WEBHOOK_URL = 'https://alpha-bot-zkn3.onrender.com/' + API_TOKEN

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

usernames_file = "usernames.txt"
messages_to_send = []

# خوش‌آمدگویی در پی‌وی
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_photo(message.chat.id,
        photo='https://raw.githubusercontent.com/Alpharobocup/alpha_bot/main/photo16500660682.jpg',
        caption="🌀 به ربات آلفا خوش آمدید!\n\n📘 راهنما:\n• تایپ «تقویم» برای مشاهده تاریخ\n• تایپ «+ [ساعت] پیام» برای ارسال زمان‌بندی شده\n• تایپ «لام» برای خوش‌آمد و لوگو"
    )

# خوش‌آمد با کلمه "لام"
@bot.message_handler(func=lambda m: m.text and "سلام" in m.text.lower())
def lamm(message):
    send_welcome(message)

# حذف پیام و پیام "حذف"
@bot.message_handler(func=lambda m: m.reply_to_message and "حذف" in m.text.lower())
def delete_message(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)  # حذف پیام "حذف"
        bot.delete_message(message.chat.id, message.reply_to_message.message_id)  # حذف پیام اصلی
    except:
        pass

# تقویم فارسی و میلادی
@bot.message_handler(func=lambda m: "تقویم" in m.text.lower())
def calendar_info(message):
    today = datetime.datetime.now()
    try:
        from persiantools.jdatetime import JalaliDate
        shamsi = JalaliDate.today()
        bot.reply_to(message, f"📅 تاریخ امروز:\nمیلادی: {today.strftime('%Y-%m-%d')}\nشمسی: {shamsi}")
    except:
        bot.reply_to(message, f"📅 تاریخ امروز:\nمیلادی: {today.strftime('%Y-%m-%d')}")

# ذخیره یوزرنیم‌ها
@bot.message_handler(func=lambda m: True, content_types=['text'])
def all_messages(message):
    try:
        if message.chat.type != 'private':
            username = message.from_user.username or f"[NoUsername-{message.from_user.id}]"
            with open(usernames_file, "a") as f:
                f.write(username + '\n')
    except:
        pass

    # ارسال اطلاعات کاربران به ادمین خاص
    try:
        sender = message.from_user
        info = f"👤 پیام جدید از {sender.first_name} (@{sender.username} | {sender.id})"
        bot.send_message(OWNER_ID, info)
    except:
        pass

    # زمان‌بندی پیام
    if message.text.startswith('+'):
        try:
            time_part, msg_part = message.text[1:].split(' ', 1)
            messages_to_send.append((time_part.strip(), msg_part, message.chat.id))
            bot.reply_to(message, f"✅ پیام زمان‌بندی شد برای {time_part.strip()}")
        except:
            bot.reply_to(message, "❌ فرمت درست نیست. مثلا: +06:00 صبح بخیر")

# پنل ادمین
@bot.message_handler(commands=['panel'])
def admin_panel(message):
    if message.from_user.id == OWNER_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("ارسال صبح بخیر", callback_data='goodmorning'))
        markup.add(types.InlineKeyboardButton("ارسال شب بخیر", callback_data='goodnight'))
        bot.send_message(message.chat.id, "🎛 پنل مدیریت", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.from_user.id != OWNER_ID:
        return
    if call.data == 'goodmorning':
        bot.send_message(call.message.chat.id, "☀️ صبح بخیر رفقا!")
    elif call.data == 'goodnight':
        bot.send_message(call.message.chat.id, "🌙 شب خوش دوستان!")

# تایمر چک پیام‌های زمان‌بندی شده
import threading
def scheduled_loop():
    while True:
        now = datetime.datetime.now().strftime("%H:%M")
        for sched in messages_to_send[:]:
            if sched[0] == now:
                try:
                    bot.send_message(sched[2], sched[1])
                    messages_to_send.remove(sched)
                except:
                    pass
        time.sleep(30)

threading.Thread(target=scheduled_loop, daemon=True).start()

# ====== اجرای Webhook روی Render ======
@app.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

@app.route('/')
def webhook():
    return "ربات آلفا فعال است."

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=port)
