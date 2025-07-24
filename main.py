import telebot
import os
BOT_TOKEN = "7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo"
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام، به ربات آلفا خوش اومدی!")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, message.text)
import random

# لیست چالش‌ها
truths = [
    "🧠 آخرین باری که دروغ گفتی کی بود؟",
    "📅 بزرگترین راز زندگیت چیه؟",
    "😳 تا حالا به کسی حسودی کردی؟ به کی؟",
    "💬 تا حالا عاشق شدی؟ راستشو بگو!",
]

dares = [
    "😈 برو به یکی بگو دوستش داری (هر کی!)",
    "📷 یه عکس از خودت همین الان بفرست.",
    "🗣 برو تو گروه بگو «من همه چیزو خراب کردم 😭»",
    "🎤 یه آهنگ بخون و ویسشو بفرست!",
]

# وقتی کاربر نوشت /truthordare
@bot.message_handler(commands=['jorat'])
def truth_or_dare(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("جرئت 💪", "حقیقت 🧠")
    bot.send_message(message.chat.id, "بازی شروع شد! یکی رو انتخاب کن:", reply_markup=markup)

# واکنش به دکمه‌ها
@bot.message_handler(func=lambda msg: msg.text in ["جرئت 💪", "حقیقت 🧠"])
def send_game_item(message):
    if message.text == "جرئت 💪":
        dare = random.choice(dares)
        bot.send_message(message.chat.id, f"🎯 چالش تو:\n{dare}")
    else:
        truth = random.choice(truths)
        bot.send_message(message.chat.id, f"📜 سوال تو:\n{truth}")

bot.polling()
