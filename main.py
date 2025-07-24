import os
import telebot
from http.server import BaseHTTPRequestHandler, HTTPServer
from telebot import types
from flask import Flask, request

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
WEBHOOK_HOST = 'https://alpha-bot-zkn3.onrender.com'
WEBHOOK_PATH = f"/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! به ربات ساده من خوش اومدی 😊")

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
with HTTPServer(("", PORT), WebhookHandler) as server:
    print(f"ربات در پورت {PORT} اجرا شد...")
    server.serve_forever()
import telebot
from flask import Flask, request

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)


# روت اصلی برای دریافت پیام از وب‌هوک
@app.route('/' + API_TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

# روت ساده برای تست فعال بودن
@app.route("/")
def webhook():
    return "ربات فعال است"

# منو و پیام شروع
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("🧾 درباره ربات")
    btn2 = types.KeyboardButton("➕ افزودن به گروه")
    btn3 = types.KeyboardButton("🔁 تکرار جمله")
    btn4 = types.KeyboardButton("⏳ به‌زودی...")
    markup.add(btn1, btn2)
    markup.add(btn3, btn4)
    bot.send_message(message.chat.id, "سلام! به ربات خوش اومدی، یکی از گزینه‌ها رو انتخاب کن 👇", reply_markup=markup)

# پاسخ به دکمه‌ها
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    if message.text == "🧾 درباره ربات":
        bot.reply_to(message, "این ربات ساده برای پاسخ‌گویی اولیه و تست ساخته شده توسط تیم آلفا ✨")
    elif message.text == "➕ افزودن به گروه":
        bot.reply_to(message, "برای افزودن ربات به گروه از لینک زیر استفاده کن:\n" +
                      f"https://t.me/{bot.get_me().username}?startgroup=add")
    elif message.text == "🔁 تکرار جمله":
        bot.send_message(message.chat.id, "جمله‌ای بفرست تا ۵ بار برات تکرارش کنم.")
        bot.register_next_step_handler(message, repeat_text)
    elif message.text == "⏳ به‌زودی...":
        bot.reply_to(message, "این قابلیت به‌زودی فعال خواهد شد 😉")

def repeat_text(message):
    text = message.text
    repeated = "\n".join([text]*5)
    bot.send_message(message.chat.id, repeated

# اجرای اپلیکیشن
if __name__ == "__main__":
    import os
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{API_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
