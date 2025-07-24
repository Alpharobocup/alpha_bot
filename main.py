import telebot, jdatetime, requests, json, datetime
from flask import Flask, request

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOx'
bot = telebot.TeleBot(API_TOKEN)
WEBHOOK_HOST = 'https://alpha-bot-zkn3.onrender.com'
WEBHOOK_PATH = f'/bot{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

app = Flask(__name__)
group_settings = {}

# ذخیره تنظیمات برای هر گروه
def get_group(chat_id):
    if chat_id not in group_settings:
        group_settings[chat_id] = {
            'owner_id': None,
            'greet_enabled': True,
            'require_add': True
        }
    return group_settings[chat_id]

# --- شروع ---

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🤖 ربات فعال شد. لطفاً در گروه ادمینم کن تا بتونم کار کنم.")

# --- شناسایی مالک گروه ---
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def group_init(msg):
    chat_id = msg.chat.id
    setting = get_group(chat_id)
    if setting['owner_id'] is None:
        admins = bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.status == 'creator':
                setting['owner_id'] = admin.user.id
                bot.send_message(chat_id, f"👑 مالک گروه شناسایی شد: {admin.user.first_name}")
                break

# --- خوش‌آمدگویی ---
@bot.chat_member_handler()
def greet_user(event):
    chat_id = event.chat.id
    setting = get_group(chat_id)
    if setting['greet_enabled'] and event.new_chat_member:
        user = event.new_chat_member.user
        name = f"[{user.first_name}](tg://user?id={user.id})" if user.username is None else f"@{user.username}"
        bot.send_message(chat_id, f"🎉 به گروه خوش آمدی {name}!", parse_mode="Markdown")

# --- حذف پیام‌های سیستمی ---
@bot.message_handler(content_types=['new_chat_members', 'left_chat_member'])
def delete_sys_msg(msg):
    try:
        bot.delete_message(msg.chat.id, msg.message_id)
    except:
        pass

# --- جستجوی گوگل ---
@bot.message_handler(commands=['google'])
def google_search(msg):
    query = msg.text.split(' ', 1)
    if len(query) == 2:
        q = query[1]
        link = f"https://www.google.com/search?q={q.replace(' ', '+')}"
        bot.reply_to(msg, f"🔍 نتیجه جستجو:\n{link}")
    else:
        bot.reply_to(msg, "استفاده: /google سوال شما")

# --- منوی بزودی ---
@bot.message_handler(commands=['be_zoodi'])
def be_zoodi(msg):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btns = ['📅 تقویم امروز', '🕋 اوقات شرعی', '📜 شعر', '😂 جوک']
    markup.add(*btns)
    bot.send_message(msg.chat.id, "💡 قابلیت‌های جدید:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == '📅 تقویم امروز')
def show_date(msg):
    today = jdatetime.date.today()
    bot.send_message(msg.chat.id, f"📅 تاریخ امروز: {today.strftime('%A %Y/%m/%d')}")

@bot.message_handler(func=lambda m: m.text == '🕋 اوقات شرعی')
def show_azan(msg):
    city = "Tehran"
    try:
        res = requests.get(f"https://api.keybit.ir/owghat/?city={city}")
        data = res.json()
        bot.send_message(msg.chat.id, f"🌅 طلوع: {data['Sunrise']}\n🌇 غروب: {data['Sunset']}")
    except:
        bot.send_message(msg.chat.id, "❌ دریافت اطلاعات ناموفق بود")

@bot.message_handler(func=lambda m: m.text == '😂 جوک')
def joke(msg):
    bot.send_message(msg.chat.id, "😂 یه جوک: چرا کامپیوتر خسته نمیشه؟ چون همیشه ریفرش میشه!")

@bot.message_handler(func=lambda m: m.text == '📜 شعر')
def poem(msg):
    bot.send_message(msg.chat.id, "📜 شعری زیبا:\nبه نام خداوند جان و خرد،\nکزین برتر اندیشه برنگذرد.")

# --- پاسخ مناسبتی (مثلاً روز برنامه‌نویس) ---
def send_special_messages():
    now = jdatetime.date.today()
    if now.month == 6 and now.day == 13:
        for chat_id in group_settings:
            bot.send_message(chat_id, "💻 روز برنامه‌نویس مبارک! 👨‍💻👩‍💻")

# --- حذف با ریپلای + حذف ---
@bot.message_handler(func=lambda m: m.reply_to_message and m.text.lower() == 'حذف')
def kick_user(msg):
    try:
        user_id = msg.reply_to_message.from_user.id
        bot.kick_chat_member(msg.chat.id, user_id)
        bot.send_message(msg.chat.id, "❌ کاربر حذف شد.")
    except:
        bot.send_message(msg.chat.id, "⚠️ خطا در حذف کاربر.")

# --- سکوت دادن با عدد ---
@bot.message_handler(func=lambda m: m.reply_to_message and m.text.lower().startswith('سکوت'))
def silence_user(msg):
    try:
        parts = msg.text.split()
        seconds = int(parts[1]) * 60
        user_id = msg.reply_to_message.from_user.id
        until = datetime.datetime.now() + datetime.timedelta(seconds=seconds)
        bot.restrict_chat_member(msg.chat.id, user_id, until_date=until)
        bot.send_message(msg.chat.id, f"🔇 کاربر تا {seconds//60} دقیقه در سکوت است.")
    except:
        bot.send_message(msg.chat.id, "⚠️ خطا در سکوت دادن.")

# --- اجبار به ادد ---
@bot.message_handler(func=lambda m: True)
def check_add(msg):
    chat_id = msg.chat.id
    setting = get_group(chat_id)
    if setting.get("require_add") and msg.from_user.id != setting["owner_id"]:
        member_count = bot.get_chat_member_count(chat_id)
        user_status = bot.get_chat_member(chat_id, msg.from_user.id)
        if user_status.status == 'member':
            bot.delete_message(chat_id, msg.message_id)
            bot.send_message(chat_id, "⛔️ اول یک نفر را ادد کن تا بتوانی پیام بدهی!")

# --- وب‌هوک Flask ---
@app.route('/', methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return 'ok', 200

@app.route('/', methods=['GET'])
def index():
    return 'ربات روشنه.'

# --- تنظیم وب‌هوک ---
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# --- اجرا ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
