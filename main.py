import os
import telebot
from telebot import types
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import jdatetime
import requests

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
WEBHOOK_HOST = 'https://alpha-bot-zkn3.onrender.com'
WEBHOOK_PATH = f"/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

bot = telebot.TeleBot(API_TOKEN)

# دکمه‌های منوی اصلی
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("✨ بزودی", "جستجوی گوگل 🔎")
    return markup

# دکمه‌های منوی بزودی
def upcoming_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("📆 تقویم ایرانی", "☀️ اوقات شرعی")
    markup.row("🔄 تبدیل تاریخ", "😂 جوک بامزه")
    markup.row("📝 شعر تصادفی", "🆔 کارت ملی")
    markup.row("↩️ بازگشت")
    return markup

# خوش‌آمدگویی
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "سلام! خوش اومدی 🌟", reply_markup=main_menu())

# مدیریت پیام‌های کاربر
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text

    if text == "✨ بزودی":
        bot.send_message(message.chat.id, "قابلیت‌های جدید:", reply_markup=upcoming_menu())

    elif text == "↩️ بازگشت":
        bot.send_message(message.chat.id, "بازگشت به منوی اصلی:", reply_markup=main_menu())

    elif text == "📆 تقویم ایرانی":
        today = jdatetime.date.today().strftime("%A %d %B %Y")
        bot.send_message(message.chat.id, f"📆 امروز: {today}")

    elif text == "☀️ اوقات شرعی":
        # پیش‌فرض شهر تهران (برای ساده‌سازی)
        response = requests.get("https://api.keybit.ir/time/")
        if response.ok:
            data = response.json()
            sunrise = data['data']['sunrise']
            sunset = data['data']['sunset']
            bot.send_message(message.chat.id, f"☀️ طلوع: {sunrise}\n🌙 غروب: {sunset}")
        else:
            bot.send_message(message.chat.id, "❌ خطا در دریافت اوقات شرعی")

    elif text == "🔄 تبدیل تاریخ":
        now = datetime.now()
        j_now = jdatetime.date.fromgregorian(date=now)
        bot.send_message(message.chat.id, f"تاریخ شمسی: {j_now.strftime('%A %d %B %Y')}")

    elif text == "😂 جوک بامزه":
        res = requests.get("https://api.codebazan.ir/jok/")
        bot.send_message(message.chat.id, res.text)

    elif text == "📝 شعر تصادفی":
        res = requests.get("https://api.codebazan.ir/poem/")
        bot.send_message(message.chat.id, res.text)

    elif text == "🆔 کارت ملی":
        bot.send_message(message.chat.id, "عدد ۱۰ رقمی کارت ملی رو بفرست... (درحال ساخت)")

    elif text.startswith("جستجوی گوگل") or text.startswith("🔎"):
        query = text.replace("جستجوی گوگل", "").replace("🔎", "").strip()
        if not query:
            bot.send_message(message.chat.id, "متن مورد نظر برای جستجو رو بنویس بعد از این دکمه!")
        else:
            bot.send_message(message.chat.id, f"🔗 https://www.google.com/search?q={query.replace(' ', '+')}")

# خوش‌آمدگویی هنگام اضافه شدن به گروه
@bot.chat_member_handler()
def welcome_member(update: types.ChatMemberUpdated):
    new_member = update.new_chat_member.user
    if update.new_chat_member.status == "member":
        name = new_member.first_name
        uid = new_member.id
        mention = f"[{name}](tg://user?id={uid})"
        bot.send_message(update.chat.id, f"🎉 خوش اومدی {mention}!", parse_mode="Markdown")

# حذف پیام‌های سیستمی ورود/خروج/تغییرات
@bot.message_handler(content_types=['new_chat_members', 'left_chat_member'])
def delete_system_messages(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

# تنظیم وب‌هوک
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# وب‌سرور برای وب‌هوک
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
    print(f"✅ ربات در پورت {PORT} اجرا شد...")
    server.serve_forever()
