import telebot
import os
BOT_TOKEN = "7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo"
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام، به ربات خوش اومدی!")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, message.text)

bot.polling()
