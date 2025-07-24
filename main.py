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


