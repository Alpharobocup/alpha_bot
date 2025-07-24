import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import telebot
from telebot import types

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
WEBHOOK_HOST = 'https://alpha-bot-zkn3.onrender.com'
WEBHOOK_PATH = f'/{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

bot = telebot.TeleBot(API_TOKEN)

# وضعیت‌ها
repeat_mode = {}
soon_menu_mode = {}

# منوی شروع
@bot.message_handler(commands=['start'])
def send_welcome(message):
    soon_menu_mode[message.chat.id] = False
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        types.KeyboardButton("🧾 درباره ربات"),
        types.KeyboardButton("➕ افزودن به گروه"),
    )
    markup.add(
        types.KeyboardButton("🔁 تکرار جمله"),
        types.KeyboardButton("⏳ به‌زودی...")
    )
    bot.send_message(message.chat.id, "سلام! یکی از گزینه‌ها رو انتخاب کن 👇", reply_markup=markup)

# جستجوی گوگل
@bot.message_handler(commands=['google'])
def google_search(message):
    query = message.text.replace('/google', '').strip()
    if query:
        link = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        bot.reply_to(message, f"🔍 نتیجه جستجو:\n{link}")
    else:
        bot.reply_to(message, "❗ لطفاً بعد از /google عبارت مورد نظر رو بنویس.")

# خوش‌آمدگویی اعضای جدید
@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        name = f"[{new_member.first_name}](tg://user?id={new_member.id})"
        bot.send_message(message.chat.id, f"🎉 خوش اومدی {name}!", parse_mode="Markdown")

# حذف پیام‌های سیستمی (کاربر رفت / گروه تغییر کرد و...)
@bot.message_handler(content_types=['left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo', 'group_chat_created'])
def delete_system_messages(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass  # اگر حذف نشد، نادیده بگیر

# مدیریت دکمه‌ها و منو
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    chat_id = message.chat.id

    # تکرار جمله
    if repeat_mode.get(chat_id, False):
        repeated = "\n".join([message.text] * 5)
        bot.send_message(chat_id, repeated)
        repeat_mode[chat_id] = False
        return

    # حالت "به‌زودی..."
    if soon_menu_mode.get(chat_id, False):
        if message.text == "گزینه ۱":
            bot.send_message(chat_id, "تو گزینه ۱ رو زدی!")
        elif message.text == "گزینه ۲":
            bot.send_message(chat_id, "تو گزینه ۲ رو زدی!")
        elif message.text == "گزینه ۳":
            bot.send_message(chat_id, "تو گزینه ۳ رو زدی!")
        elif message.text == "بازگشت":
            soon_menu_mode[chat_id] = False
            send_welcome(message)
        else:
            bot.send_message(chat_id, "لطفاً یکی از گزینه‌ها رو انتخاب کن یا «بازگشت» رو بزن.")
        return

    # منوی اصلی
    if message.text == "🧾 درباره ربات":
        bot.send_message(chat_id, "این ربات ساده توسط تیم آلفا ساخته شده ✨")
    elif message.text == "➕ افزودن به گروه":
        keyboard = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(
            "افزودن ربات به گروه",
            url=f"https://t.me/{bot.get_me().username}?startgroup=true"
        )
        keyboard.add(btn)
        bot.send_message(chat_id, "روی دکمه زیر بزن:", reply_markup=keyboard)
    elif message.text == "🔁 تکرار جمله":
        bot.send_message(chat_id, "جمله‌ای بفرست تا ۵ بار تکرارش کنم.")
        repeat_mode[chat_id] = True
    elif message.text == "⏳ به‌زودی...":
        soon_menu_mode[chat_id] = True
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(
            types.KeyboardButton("گزینه ۱"),
            types.KeyboardButton("گزینه ۲")
        )
        markup.add(
            types.KeyboardButton("گزینه ۳"),
            types.KeyboardButton("بازگشت")
        )
        bot.send_message(chat_id, "صفحه جدید، یکی از گزینه‌ها رو بزن 👇", reply_markup=markup)
    else:
        bot.send_message(chat_id, "❗ لطفاً یکی از دکمه‌ها رو انتخاب کن.")

# تنظیم وب‌هوک
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# هندلر وب‌هوک
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

# اجرا
PORT = int(os.environ.get('PORT', 8443))

if __name__ == '__main__':
    print(f"ربات روی پورت {PORT} اجرا شد...")
    with HTTPServer(("", PORT), WebhookHandler) as server:
        server.serve_forever()
