import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot
from telebot import types

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
WEBHOOK_HOST = 'https://alpha-bot-zkn3.onrender.com'  # مثلا 
WEBHOOK_PATH = f'/{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

bot = telebot.TeleBot(API_TOKEN)

# ذخیره وضعیت تکرار جمله برای هر چت
repeat_mode = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🧾 درباره ربات")
    btn2 = types.KeyboardButton("➕ افزودن به گروه")
    btn3 = types.KeyboardButton("🔁 تکرار جمله")
    btn4 = types.KeyboardButton("⏳ به‌زودی...")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    bot.send_message(message.chat.id, "سلام! یکی از گزینه‌ها رو انتخاب کن 👇", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id

    # اگر در حالت تکرار جمله باشیم و پیام معمولیه
    if repeat_mode.get(chat_id, False):
        text = message.text
        repeated = "\n".join([text]*5)
        bot.send_message(chat_id, repeated)
        repeat_mode[chat_id] = False
        return

    if message.text == "🧾 درباره ربات":
        bot.send_message(chat_id, "این ربات ساده برای پاسخ‌گویی اولیه و تست ساخته شده توسط تیم آلفا ✨")
    elif message.text == "➕ افزودن به گروه":
        bot.send_message(chat_id, f"برای افزودن ربات به گروه از این لینک استفاده کن:\nhttps://t.me/{bot.get_me().username}?startgroup=true")
    elif message.text == "🔁 تکرار جمله":
        bot.send_message(chat_id, "جمله‌ای بفرست تا ۵ بار برات تکرارش کنم.")
        repeat_mode[chat_id] = True
    elif message.text == "⏳ به‌زودی...":
        bot.send_message(chat_id, "این قابلیت به‌زودی فعال خواهد شد 😉")
    else:
        bot.send_message(chat_id, "لطفاً یکی از دکمه‌ها رو بزن :)")

# تنظیم وب‌هوک
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == WEBHOOK_PATH:
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            update = telebot.types.Update.de_json(body.decode("utf-8"))
            bot.process_new_updates([update])
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

PORT = int(os.environ.get('PORT', 8443))

if __name__ == '__main__':
    print(f"ربات روی پورت {PORT} اجرا شد...")
    with HTTPServer(("", PORT), WebhookHandler) as server:
        server.serve_forever()
