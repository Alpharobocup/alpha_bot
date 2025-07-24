import telebot
import os

TOKEN = os.environ.get("7918282843:AAFR3gZebQoctyMOcvI8L3cI5jZZcD0kOxo")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام، به ربات آلفا خوش اومدی!")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, message.text)

bot.polling()
