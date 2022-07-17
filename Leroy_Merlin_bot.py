import logging
import os
import time

from dotenv import load_dotenv
from telegram.ext import CommandHandler, Updater

load_dotenv()

TOKEN = os.getenv('TOKEN')


def start(update, context):
    """The method starts working when the bot starts."""
    chat = update.effective_chat
    username = update.message.chat.username
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}, я помогу тебе быстро узнать сколько ты заработал '
        'за месяц в Леруа Мерлен'.format(username)
    )
    context.bot.send_message(
        chat_id=chat.id,
        text='Чтобы получить инструкцию по работе бота, нажми на команду '
        '/help'
    )


def main():
    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(CommandHandler('start', start))

    updater.start_polling()

    while True:
        logging.basicConfig(level=logging.INFO)
        logging.info('Раз в 10 минут и сообщение отправляется')
        time.sleep(600)


if __name__ == '__main__':
    main()
