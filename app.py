import telebot
import requests
import json
import os
import logging
from telebot import types

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
  welcome_message = (
    f'Olá {message.from_user.first_name}. Tudo bem?\n\n'
    'Veja o que posso fazer por você:\n'
    '1. /cep - Consultar informações de um CEP\n'
    '2. /pessoa - Gerar uma pessoa fictícia com IA\n\n'
    'Escreva abaixo o comando que deseja utilizar ou clique diretamente acima.'
  )
  bot.send_message(chat_id=message.from_user.id, text=welcome_message)

@bot.message_handler(commands=['cep'])
def process_cep_input(message):
  print('[DEBUG]: process_cep_input()')

  try:
    print('[DEBUG] message.text:', message.text)

    items = message.text.split()
    if len(items) < 2 and items[0] == '/cep':
      bot.send_message(chat_id=message.from_user.id, text='É necessário informar apenas números - ex: 0100100')
      bot.register_next_step_handler(message, process_cep_input)
      return
    
    cep_solicitado = items[-1]

    url_api = f'https://viacep.com.br/ws/{cep_solicitado}/json/'
    print('[DEBUG] url_api:', url_api)

    response = requests.get(url_api)
    print('[DEBUG] response.status_code:', response.status_code)
    print('[DEBUG] response.text:', response.text)

    if response.status_code == 200:
      print('[DEBUG]: STATUS OK')
      dicionario = response.json()

      mensagem = 'Essas são as informações do CEP solicitado!\n\nCEP: {}\nLogradouro: {}\nBairro: {}\nCidade: {}\nEstado: {}\nDDD da Região: {}'
      markup = create_main_menu_button()
      bot.send_chat_action(chat_id=message.from_user.id, action='typing')
      bot.send_message(chat_id=message.from_user.id, text=mensagem.format(dicionario['cep'], dicionario['logradouro'], dicionario['bairro'], dicionario['localidade'], dicionario['uf'], dicionario['ddd']), reply_to_message_id=message.message_id, reply_markup=markup)

    else:
      bot.send_message(chat_id=message.from_user.id, text='🚫 Dados incorretos. Por favor, informe um CEP válido.', reply_to_message_id=message.message_id)
      bot.register_next_step_handler(message, process_cep_input)

  except Exception as ex:
    print('[DEBUG] Exception:', ex)
    bot.send_message(chat_id=message.from_user.id, text='🚫 Dados incorretos. Por favor, informe um CEP válido.', reply_to_message_id=message.message_id)
    bot.register_next_step_handler(message, process_cep_input)

@bot.message_handler(commands=['pessoa'])
def handler_person_ia(message):
  print('[DEBUG]: handler_person_ia()')

  try:
    markup = types.InlineKeyboardMarkup()
    markup.add(
      types.InlineKeyboardButton('🖼️ Gerar Pessoa com IA', callback_data='/chatbot ia person'),
      types.InlineKeyboardButton('Menu Principal', callback_data='/chatbot main menu'),
      row_width=1
    )
    bot.send_message(chat_id=message.from_user.id, text='Escolha uma das opções abaixo:'.format(message.from_user.first_name), reply_markup=markup, reply_to_message_id=message.message_id)

  except Exception as ex:
    print('[DEBUG] Exception:', ex)

    bot.send_message(chat_id=message.from_user.id, text='Ocorreu um erro ao gerar a imagem, escolha uma nova opção.', reply_to_message_id=message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
  print('[DEBUG] callback_handler:', call.data)

  if call.data == '/chatbot main menu':
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)
    handler_start(call)

  elif call.data == '/chatbot ia person':
    markup = create_main_menu_button()

    bot.send_chat_action(chat_id=call.from_user.id, action='typing')
    bot.delete_message(chat_id=call.from_user.id, message_id=call.message.message_id)

    url_api = 'https://www.thispersondoesnotexist.com/'
    print('[DEBUG] url_api:', url_api)
    
    try:
      with open('{}_person.png'.format(call.from_user.id), 'wb') as imagem:
        response = requests.get(url_api)
        print('[DEBUG] response.status_code:', response.status_code)
        print('[DEBUG] response.text:', response.text)

        imagem.write(response.content)
        bot.send_photo(chat_id=call.from_user.id, photo=open('{}_person.png'.format(call.from_user.id), 'rb'), caption='Imagem gerada com Inteligência Artificial', reply_markup=markup)
        print('[DEBUG]: Image sent successfully')

    except Exception as ex:
      print('[DEBUG] Exception:', ex)

      bot.send_message(chat_id=call.from_user.id, text='Ocorreu um erro ao gerar a imagem, tente novamente mais tarde.', reply_markup=create_main_menu_button())

if __name__ == '__main__':
  bot.polling()