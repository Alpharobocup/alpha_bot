import telebot
from flask import Flask, request
import random, os, re
import jdatetime
from datetime import datetime, timedelta

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
bot = telebot.TeleBot(API_TOKEN)
WEBHOOK_HOST = 'https://alpha-bot-zkn3.onrender.com'
WEBHOOK_PATH = f'/bot{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

app = Flask(__name__)
group_settings = {}

def get_group(chat_id):
    if chat_id not in group_settings:
        group_settings[chat_id] = {
            'owner_id': None
        }
    return group_settings[chat_id]

# شناسایی مالک
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def identify_owner(message):
    chat_id = message.chat.id
    setting = get_group(chat_id)
    if setting['owner_id'] is None:
        try:
            admins = bot.get_chat_administrators(chat_id)
            for admin in admins:
                if admin.status == 'creator':
                    setting['owner_id'] = admin.user.id
                    bot.send_message(chat_id, f"👑 مالک گروه شناسایی شد: {admin.user.first_name}")
        except: pass

# خوش‌آمدگویی
@bot.chat_member_handler()
def welcome_new_member(update):
    chat_id = update.chat.id
    user = update.new_chat_member.user
    name = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
    bot.send_message(chat_id, f"🎉 خوش آمدی {name}!", parse_mode='Markdown')

# حذف پیام‌های سیستمی
@bot.message_handler(content_types=[
    'new_chat_members', 'left_chat_member',
    'new_chat_title', 'new_chat_photo'
])
def delete_system_messages(msg):
    try:
        bot.delete_message(msg.chat.id, msg.message_id)
    except: pass

# شماره رندوم
@bot.message_handler(commands=['number'])
def send_random_number(msg):
    ops = {
        'ایرانسل': ['0935', '0936', '0937'],
        'همراه اول': ['0910', '0911', '0990'],
        'رایتل': ['0920', '0921']
    }
    op = random.choice(list(ops.keys()))
    prefix = random.choice(ops[op])
    number = prefix + ''.join(str(random.randint(0,9)) for _ in range(7))
    bot.reply_to(msg, f"📱 شماره رندوم {op}:\n{number}")

# حذف کاربر با ریپلای «دیلیت»
@bot.message_handler(func=lambda m: m.reply_to_message and m.text.lower() == 'دیلیت')
def kick_user(m):
    admins = bot.get_chat_administrators(m.chat.id)
    if m.from_user.id in [a.user.id for a in admins]:
        try:
            bot.ban_chat_member(m.chat.id, m.reply_to_message.from_user.id)
            bot.unban_chat_member(m.chat.id, m.reply_to_message.from_user.id)  # برای کیک شدن نه بن
            bot.reply_to(m, "❌ کاربر حذف شد.")
        except:
            bot.reply_to(m, "⚠️ خطا در حذف کاربر.")
    else:
        bot.reply_to(m, "⛔ فقط ادمین می‌تونه کسی رو حذف کنه.")

# حذف پیام با «حذف»
@bot.message_handler(func=lambda m: m.reply_to_message and m.text.lower() == 'حذف')
def delete_message(m):
    try:
        bot.delete_message(m.chat.id, m.reply_to_message.message_id)
        bot.delete_message(m.chat.id, m.message_id)
    except:
        bot.reply_to(m, "⚠️ خطا در حذف پیام.")

# سکوت با «سکوت [عدد]»
@bot.message_handler(func=lambda m: m.reply_to_message and m.text.lower().startswith('سکوت'))
def mute_user(m):
    admins = bot.get_chat_administrators(m.chat.id)
    if m.from_user.id not in [a.user.id for a in admins]:
        return bot.reply_to(m, "⛔ فقط ادمین‌ها مجازند.")
    try:
        seconds = int(re.findall(r'\d+', m.text)[0])
        until = datetime.utcnow() + timedelta(seconds=seconds)
        bot.restrict_chat_member(
            m.chat.id,
            m.reply_to_message.from_user.id,
            permissions=telebot.types.ChatPermissions(can_send_messages=False),
            until_date=until
        )
        bot.reply_to(m, f"🔇 کاربر به مدت {seconds} ثانیه ساکت شد.")
    except:
        bot.reply_to(m, "⚠️ خطا در سکوت یا عدد وارد نشده.")

# تاریخ شمسی و ساعت
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['تقویم', 'روز', 'ساعت', 'زمان'])
def date_time(m):
    now = jdatetime.datetime.now()
    greg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bot.reply_to(m, f"📅 امروز: {now.strftime('%Y/%m/%d - %A')}\n🕰 ساعت: {now.strftime('%H:%M:%S')}\n📆 میلادی: {greg}")

# ارتقاء به ادمین توسط مالک
@bot.message_handler(func=lambda m: m.text and m.text.startswith('ادمین'))
def promote_admin(m):
    chat_id = m.chat.id
    setting = get_group(chat_id)
    if setting['owner_id'] != m.from_user.id:
        return bot.reply_to(m, "⛔ فقط مالک گروه می‌تونه ادمین کنه.")
    
    match = re.search(r'@?(\w+)', m.text.split('ادمین')[1].strip())
    if not match:
        return bot.reply_to(m, "🆔 آیدی را درست وارد کن.")

    username = match.group(1)
    try:
        user = bot.get_chat_member(chat_id, f"@{username}").user
        admins = bot.get_chat_administrators(chat_id)
        if user.id in [a.user.id for a in admins]:
            return bot.reply_to(m, "✅ این فرد قبلاً ادمین است.")
        bot.promote_chat_member(chat_id, user.id,
            can_delete_messages=True,
            can_restrict_members=True,
            can_promote_members=False,
            can_change_info=False
        )
        bot.reply_to(m, f"👮‍♂️ {user.first_name} به ادمین ارتقا یافت.")
    except:
        bot.reply_to(m, "❌ خطا در ارتقا یا کاربر پیدا نشد.")

# Flask Webhook
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return 'ربات فعال است.'

def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

if __name__ == '__main__':
    setup_webhook()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
