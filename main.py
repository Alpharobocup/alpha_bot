import os
import telebot
from http.server import BaseHTTPRequestHandler, HTTPServer

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

# دستورات رباتت
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! من آماده‌ام :)")

# اجرای اپلیکیشن
if __name__ == "__main__":
    import os
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{API_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))


