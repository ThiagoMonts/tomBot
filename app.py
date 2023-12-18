import telebot
import requests
import os
import logging
from telebot import types
from dotenv import load_dotenv
import random
import json

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = telebot.TeleBot(token=TELEGRAM_BOT_TOKEN, parse_mode='HTML')

telebot.logger.setLevel(logging.INFO)

def create_main_menu_button():
  markup = types.InlineKeyboardMarkup()
  markup.add(
    types.InlineKeyboardButton('Menu Principal', callback_data='/chatbot main menu')
  )
  return markup

@bot.message_handler(commands=['start'])
def handler_start(message):
  markup = types.InlineKeyboardMarkup()
  markup.add(
    types.InlineKeyboardButton('Verificar status', callback_data='/chatbot estou com sorte'),
    row_width=1
  )

  welcome_message = (
    f'Olá {message.from_user.first_name}. Tudo bem?\n\n'
    'Queria saber se o meu pedido já foi enviado. Você pode me ajudar?\n\n'
    '1. /status - Verificar status\n\n'
  )
  bot.send_message(chat_id=message.from_user.id, text=welcome_message, reply_markup=markup)

@bot.message_handler(commands=['status'])
def process_status_input(message):
  print('[DEBUG]: process_status_input()')

  try:
    print('[DEBUG] message.text:', message.text)

    markup = types.InlineKeyboardMarkup()
    markup.add(
      types.InlineKeyboardButton('Perguntar novamente', callback_data='/chatbot estou com sorte'),
      row_width=1
    )

    bot.send_message(chat_id=message.from_user.id, text='Não gostei desta justificativa, não me convenceu.', reply_markup=markup)

  except Exception as ex:
    print('[DEBUG] Exception:', ex)

    
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
  print('[DEBUG] callback_handler:', call.data)

  try:
    
    if call.data == '/chatbot estou com sorte':
      bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    
      with open('desculpas.json', 'r', encoding='utf-8') as f:
        numero = random.randint(0, 10)
        data = json.load(f)

      chave = data[f'{numero}']
      print('[DEBUG] /estou com sorte:', chave)

      bot.send_message(chat_id=call.from_user.id, text=chave, reply_markup=create_main_menu_button())

    elif call.data == '/chatbot main menu':
      handler_start(call)

  except Exception as ex:
    print('[DEBUG] Exception:', ex)

if __name__ == '__main__':
  bot.polling()