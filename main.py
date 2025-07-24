import telebot
from flask import Flask, request
import random
import os

API_TOKEN = '7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo'
bot = telebot.TeleBot(API_TOKEN)

WEBHOOK_HOST = 'https://alpha-bot-zkn3.onrender.com'
WEBHOOK_PATH = f'/bot{API_TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

app = Flask(__name__)

# ذخیره اطلاعات گروه‌ها
group_settings = {}

def get_group(chat_id):
    if chat_id not in group_settings:
        group_settings[chat_id] = {
            'owner_id': None
        }
    return group_settings[chat_id]

# شناسایی مالک گروه و اعلام به گروه
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
                    break
        except Exception as e:
            print(f"Error identifying owner: {e}")

# خوش‌آمدگویی به اعضای جدید
@bot.chat_member_handler()
def welcome_new_member(update):
    chat_id = update.chat.id
    new_user = update.new_chat_member.user
    # ساخت نام قابل کلیک
    if new_user.username:
        name = f"@{new_user.username}"
    else:
        name = f"[{new_user.first_name}](tg://user?id={new_user.id})"
    bot.send_message(chat_id, f"🎉 خوش آمدی {name}!", parse_mode='Markdown')

# حذف پیام‌های سیستمی ورود، خروج، تغییرات
@bot.message_handler(content_types=['new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo'])
def delete_system_messages(message):
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except Exception as e:
        print(f"Failed to delete system message: {e}")

# تولید شماره رندوم اپراتورها
def generate_random_number():
    operators = {
        'ایرانسل': ['0912', '0913', '0914', '0935', '0936', '0937'],
        'همراه اول': ['0911', '0910', '0990', '0991', '0992'],
        'رایتل': ['0920', '0921', '0922']
    }
    op = random.choice(list(operators.keys()))
    prefix = random.choice(operators[op])
    number = prefix + ''.join(str(random.randint(0,9)) for _ in range(7))
    return op, number

# دستور شماره رندوم
@bot.message_handler(commands=['number'])
def send_random_number(message):
    op, number = generate_random_number()
    bot.reply_to(message, f"📱 شماره رندوم {op}:\n{number}")

# وب‌هوک Flask
@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def index():
    return 'ربات فعال است.'

# تنظیم وب‌هوک (یکبار اجرا کن قبل از run)
def setup_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

if __name__ == "__main__":
    setup_webhook()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
