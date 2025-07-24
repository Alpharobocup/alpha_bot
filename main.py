import telebot
from flask import Flask, request
import random
import os
import datetime
from pytz import timezone
from persiantools.jdatetime import JalaliDateTime

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
WEBHOOK_HOST = 'https://alpha-bot-zkn3.onrender.com'  # آدرس سایتت
WEBHOOK_PATH = f'/bot{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)
group_settings = {}

def get_group(chat_id):
    if chat_id not in group_settings:
        group_settings[chat_id] = {'owner_id': None}
    return group_settings[chat_id]

# --- خوش‌آمدگویی ---
@bot.chat_member_handler()
def welcome_new_member(update):
    if update.new_chat_member.status == "member":
        user = update.new_chat_member.user
        name = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
        bot.send_message(update.chat.id, f"🎉 خوش آمدی {name}!", parse_mode='Markdown')

# --- شناسایی مالک ---
@bot.message_handler(func=lambda m: m.chat.type in ['group', 'supergroup'])
def identify_owner(message):
    chat_id = message.chat.id
    setting = get_group(chat_id)
    if setting['owner_id'] is None:
        admins = bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.status == 'creator':
                setting['owner_id'] = admin.user.id
                bot.send_message(chat_id, f"👑 مالک گروه شناسایی شد: {admin.user.first_name}")
                break

# --- حذف پیام‌های سیستمی ---
@bot.message_handler(content_types=['new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo'])
def delete_system_messages(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass

# --- شماره رندوم ---
@bot.message_handler(commands=['number'])
def send_random_number(message):
    operators = {
        'ایرانسل': ['0935', '0936', '0937'],
        'همراه اول': ['0911', '0910', '0990'],
        'رایتل': ['0920', '0921', '0922']
    }
    op = random.choice(list(operators))
    prefix = random.choice(operators[op])
    number = prefix + ''.join(str(random.randint(0,9)) for _ in range(7))
    bot.reply_to(message, f"📱 شماره رندوم {op}:\n{number}")

# --- تقویم و ساعت ---
@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['تقویم', 'تاریخ'])
def send_date(m):
    now = JalaliDateTime.now()
    bot.reply_to(m, f"📅 تاریخ امروز: {now.strftime('%Y/%m/%d')}")

@bot.message_handler(func=lambda m: m.text and m.text.lower() in ['ساعت', 'روز', 'زمان'])
def send_time(m):
    now = datetime.datetime.now(timezone('Asia/Tehran'))
    bot.reply_to(m, f"⏰ {now.strftime('%H:%M:%S')} - 🗓️ {now.strftime('%A')}")

# --- سکوت و حذف و دیلیت ---
@bot.message_handler(func=lambda m: m.reply_to_message)
def handle_reply_commands(m):
    chat_id = m.chat.id
    user_id = m.from_user.id
    replied_user = m.reply_to_message.from_user

    # حذف پیام
    if m.text.lower() == 'حذف':
        try:
            bot.delete_message(chat_id, m.reply_to_message.message_id)
            bot.delete_message(chat_id, m.message_id)
        except:
            pass

    # حذف کاربر
    elif m.text.lower() == 'دیلیت':
        try:
            admins = bot.get_chat_administrators(chat_id)
            if any(admin.user.id == user_id for admin in admins):
                if any(admin.user.id == replied_user.id for admin in admins):
                    bot.reply_to(m, "❌ کاربر ادمین است.")
                else:
                    bot.ban_chat_member(chat_id, replied_user.id)
                    bot.unban_chat_member(chat_id, replied_user.id)  # اجازه ورود دوباره
                    bot.send_message(chat_id, f"🚫 {replied_user.first_name} از گروه حذف شد.")
        except:
            pass

    # سکوت [عدد]
    elif m.text.lower().startswith('سکوت'):
        try:
            admins = bot.get_chat_administrators(chat_id)
            if any(admin.user.id == user_id for admin in admins):
                try:
                    minutes = int(m.text.split()[1])
                    until_date = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
                    bot.restrict_chat_member(
                        chat_id, 
                        replied_user.id,
                        until_date=until_date,
                        permissions=telebot.types.ChatPermissions(can_send_messages=False)
                    )
                    bot.send_message(chat_id, f"🔇 {replied_user.first_name} به مدت {minutes} دقیقه در سکوت قرار گرفت.")
                except:
                    pass
        except:
            pass

# --- دستور "ادمین [آی‌دی]" ---
@bot.message_handler(func=lambda m: m.text and m.text.startswith("ادمین"))
def promote_admin(m):
    chat_id = m.chat.id
    setting = get_group(chat_id)
    if m.from_user.id != setting['owner_id']:
        return
    try:
        user_id = int(m.text.split()[1])
        admins = bot.get_chat_administrators(chat_id)
        if any(admin.user.id == user_id for admin in admins):
            bot.reply_to(m, "🔔 این کاربر قبلاً ادمین است.")
        else:
            bot.promote_chat_member(
                chat_id,
                user_id,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_promote_members=False,
                can_pin_messages=True
            )
            bot.reply_to(m, f"✅ کاربر {user_id} به ادمین ارتقا یافت.")
    except Exception as e:
        bot.reply_to(m, "❌ ایدی نادرست یا خطا در ارتقا.")

# --- وب‌هوک ---
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return 'ربات روشن است.'

def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    setup_webhook()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
