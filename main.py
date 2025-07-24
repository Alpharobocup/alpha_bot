import os
from flask import Flask, request
import telebot
from telebot import types

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
WEBHOOK_URL = f"https://{os.environ['https://alpha-bot-zkn3.onrender.com']}/{API_TOKEN}"

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# دیتابیس موقت برای جملات یادگرفته‌شده
user_memory = {}

@app.route('/' + API_TOKEN, methods=['POST'])
def webhook_handler():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def index():
    return "ربات فعال است."

# دکمه‌ها و شروع
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🧾 درباره ربات", "🎮 جرئت یا حقیقت", "🧠 یادگیری جمله", "🔁 تکرار جمله")
    bot.send_message(message.chat.id, "سلام! به ربات آلفا خوش اومدی 👋\nیکی از گزینه‌ها رو انتخاب کن:", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id
    text = message.text

    if text == "🧾 درباره ربات":
        bot.reply_to(message, "این ربات توسط تیم آلفا ساخته شده ✨")
    elif text == "🎮 جرئت یا حقیقت":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("✅ جرئت", "❓ حقیقت")
        bot.send_message(chat_id, "کدومو انتخاب می‌کنی؟", reply_markup=markup)
    elif text == "✅ جرئت":
        dares = [
            "یه استیکر عجیب بفرست 😂", "۵ تا پشت‌سر هم ایموجی بفرست 😜", "به یکی از دوستات بگو عاشقشی 😳",
        ]
        bot.send_message(chat_id, f"جرئتت: {random.choice(dares)}")
    elif text == "❓ حقیقت":
        truths = [
            "آخرین دروغی که گفتی چی بود؟ 🤔", "تا حالا گریه کردی برای یه نفر؟ 😢", "بزرگترین ترست چیه؟ 😱",
        ]
        bot.send_message(chat_id, f"حقیقت: {random.choice(truths)}")
    elif text == "🔁 تکرار جمله":
        bot.send_message(chat_id, "یه جمله بفرست تا برات ۵ بار تکرارش کنم.")
        bot.register_next_step_handler(message, repeat_text)
    elif text == "🧠 یادگیری جمله":
        bot.send_message(chat_id, "یه جمله بفرست که بخوام یاد بگیرم.")
        bot.register_next_step_handler(message, learn_text)
    else:
        # اگر کاربر قبلاً چیزی یاد داده، همونو براش جواب بده
        if text in user_memory:
            bot.reply_to(message, user_memory[text])
        else:
            bot.reply_to(message, "نمی‌دونم چی بگم 😅")

def repeat_text(message):
    text = message.text
    repeated = "\n".join([text] * 5)
    bot.send_message(message.chat.id, repeated)

def learn_text(message):
    chat_id = message.chat.id
    text = message.text
    bot.send_message(chat_id, "خب حالا بگو اگر کسی اینو گفت، من چی بگم؟")
    bot.register_next_step_handler(message, lambda m: save_reply(text, m))

def save_reply(trigger, message):
    user_memory[trigger] = message.text
    bot.send_message(message.chat.id, "یاد گرفتم! حالا اگه کسی اینو بگه، جوابشو می‌دم.")

# اجرای اپ
if __name__ == "__main__":
    import random
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
