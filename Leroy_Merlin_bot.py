import logging
import os
import time

from dotenv import load_dotenv
from telegram import ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, Updater)

import DBHelper

load_dotenv()

CNT_SKU: int = 0  # количество SKU
CNT_HOURS: int = 0  # количество рабочих часов
NUMBER_OF_SHIFTS: int = 0  # количество смен
SALARY: float = 0.0  # зарплата
UNIT_RATE_SKU: float = 7.3  # ставка за единицу SKU
HOURLY_RATE: float = 124.0  # почасовая ставка

END, SKU, WORKING_HOURS, EDIT_SKU, SAVE_HOURLY_RATE = range(-1, 4)
CNFRM_CNT_RESET = 4

TOKEN = os.getenv('TOKEN')


def start(update, context):
    """The method starts working when the bot starts."""
    chat = update.effective_chat
    name = update.message.chat.first_name
    context.bot.send_message(
        chat_id=chat.id,
        text='Привет, {}, я помогу тебе быстро узнать сколько ты заработал '
        'за месяц в Леруа Мерлен'.format(name)
    )
    context.bot.send_message(
        chat_id=chat.id,
        text='Чтобы получить инструкцию по работе бота, нажми на команду '
        '/help'
    )
    if not DBHelper.username_db(chat_id=chat.id):
        DBHelper.add_to_db(name=name, chat_id=chat.id)


def help_description(update, context):
    """The method sends instructions to the user on how the bot works."""
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='В конце каждого рабочего дня отправляй свои данные по команде '
        '/sku\nПосле этого, в любой момент, по команде /salary ты узнаешь '
        'свою зарплату\nВ конце каждого рабочего месяца нажимай команду '
        '/reset_counter для сброса SKU и отработанных часов'
    )
    context.bot.send_message(
        chat_id=chat.id,
        text='Чтобы получить полный список команд бота, нажми на команду '
        '/commands'
    )


def bot_commands(update, context):
    """The method sends bot commands to the user."""
    chat = update.effective_chat
    context.bot.send_message(
        chat_id=chat.id,
        text='<b>Команды для подсчёта зарплаты:</b>\n/sku - Количество SKU, и '
        'рабочих часов за сегодняшний день\n/salary - Сколько заработал в '
        'этом месяце\n\n<b>Команда для сброса артикулов и часов:</b>\n'
        '/reset_counter - Сбрасывает количество SKU и отработанных часов '
        '(нажимай в новом рабочем месяце)\n\n<b>Команды изменений ставки:</b>'
        '\n/edit_sku - Изменить ставку за единицу SKU (сейчас ставка '
        f'{DBHelper.per_sku_db(chat.id)}р.)\n/edit_working_hours - Изменить '
        f'ставку за час работы (сейчас ставка {DBHelper.per_hours_db(chat.id)}'
        'р.)\n',
        parse_mode=ParseMode.HTML,
    )


def data_for_that_day(update, context):
    """The method asks to enter the count of SKU."""
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([['Отмена']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Введи количество SKU собранных сегодня',
        reply_markup=buttons
    )
    return SKU


def count_of_sku(update, context):
    """The method saves count SKU and asks you to enter working hours."""
    global CNT_SKU
    chat = update.effective_chat
    buttons = ReplyKeyboardRemove()
    save_buttons = ReplyKeyboardMarkup([['Отмена']], resize_keyboard=True)
    if update.message.text.lower() == 'отмена':
        context.bot.send_message(
            chat_id=chat.id,
            text='Данные остались без изменений ❌',
            reply_markup=buttons
        )
        return ConversationHandler.END
    elif update.message.text.isdigit():
        context.user_data[SKU] = update.message.text
        CNT_SKU = int(context.user_data[SKU])
        update.message.reply_text(
            'Напиши сколько часов работал сегодня',
            reply_markup=save_buttons
        )
        return WORKING_HOURS
    else:
        update.message.reply_text('Введи просто цифру')
        return SKU


def count_of_hours(update, context):
    """The method saves the number of working hours."""
    global CNT_HOURS, NUMBER_OF_SHIFTS, SALARY, CNT_SKU
    chat = update.effective_chat
    buttons = ReplyKeyboardRemove()
    if update.message.text.lower() == 'отмена':
        CNT_SKU = DBHelper.sku_db(chat.id)
        context.bot.send_message(
            chat_id=chat.id,
            text='Данные остались без изменений ❌',
            reply_markup=buttons
        )
        return ConversationHandler.END
    elif update.message.text.isdigit():
        context.user_data[WORKING_HOURS] = update.message.text
        CNT_HOURS = int(context.user_data[WORKING_HOURS])
        SALARY = float(CNT_SKU * UNIT_RATE_SKU + CNT_HOURS * HOURLY_RATE)
        NUMBER_OF_SHIFTS = 1
        update.message.reply_text(
            'Все данные на сегодня собраны ✅',
            reply_markup=buttons
            )
        DBHelper.edit_db(
            count_sku=DBHelper.sku_db(chat.id) + CNT_SKU,
            count_hours=DBHelper.hours_db(chat.id) + CNT_HOURS,
            count_shifts=DBHelper.shifts_db(chat.id) + NUMBER_OF_SHIFTS,
            salary=DBHelper.salary_db(chat.id) + SALARY,
            chat_id=chat.id
        )
        return ConversationHandler.END
    else:
        update.message.reply_text('Введи просто цифру')
        return WORKING_HOURS


def salary(update, context):
    """The method calculates the salary."""
    chat = update.effective_chat
    if DBHelper.salary_db(chat.id):
        context.bot.send_message(
            chat_id=chat.id,
            text=DBHelper.db_salary_information(chat_id=chat.id)
        )
    else:
        context.bot.send_message(
            chat_id=chat.id,
            text='Ты заработал ноль рублей'
        )


def edit_sku(update, context):
    """The method asks to enter a new rate per SKU."""
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([['Отмена']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Введи новую ставку за единицу SKU.\n'
        f'Сейчас она равна {DBHelper.per_sku_db(chat.id)}\n'
        'Или нажми "отмена", если передумал',
        reply_markup=buttons
    )
    return EDIT_SKU


def new_rate_per_sku(update, context):
    """The method saves the new bid per SKU."""
    global UNIT_RATE_SKU
    chat = update.effective_chat
    buttons = ReplyKeyboardRemove()
    message_error = 'Введи просто цифру(если хочешь ввести десятичное чилсло, '
    'то напиши его через точку, например "7.3")'
    try:
        if update.message.text.lower() == 'отмена':
            context.bot.send_message(
                chat_id=chat.id,
                text='Данные остались без изменений ❌',
                reply_markup=buttons
            )
            return ConversationHandler.END
        elif isinstance(float(update.message.text), float):
            context.user_data[EDIT_SKU] = update.message.text
            UNIT_RATE_SKU = float(context.user_data[EDIT_SKU])
            update.message.reply_text(
                f'Твоя ставка изменена с {DBHelper.per_sku_db(chat.id)} на '
                f'{UNIT_RATE_SKU}р. ✅',
                reply_markup=buttons
            )
            salary = float(
                DBHelper.sku_db(chat.id) * UNIT_RATE_SKU +
                DBHelper.hours_db(chat.id) * HOURLY_RATE
            )
            DBHelper.rate_sku_db(UNIT_RATE_SKU, salary, chat.id)
            return ConversationHandler.END
        else:
            update.message.reply_text(message_error)
            return EDIT_SKU
    except ValueError:
        update.message.reply_text(message_error)
        return EDIT_SKU


def edit_hourly_rate(update, context):
    """The method requests the input of a new rate per hour of work."""
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([['Отмена']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Введи новую ставку за час работы.\n'
        f'Сейчас она равна {DBHelper.per_hours_db(chat.id)}\n'
        'Или нажми "отмена", если передумал',
        reply_markup=buttons
    )
    return SAVE_HOURLY_RATE


def new_hourly_rate(update, context):
    """The method saves the new rate for the working hour."""
    global HOURLY_RATE
    chat = update.effective_chat
    buttons = ReplyKeyboardRemove()
    message_error = 'Введи просто цифру(если хочешь ввести десятичное чилсло, '
    'то напиши его через точку, например "123.7")'
    try:
        if update.message.text.lower() == 'отмена':
            context.bot.send_message(
                chat_id=chat.id,
                text='Данные остались без изменений ❌',
                reply_markup=buttons
            )
            return ConversationHandler.END
        elif isinstance(float(update.message.text), float):
            context.user_data[SAVE_HOURLY_RATE] = update.message.text
            HOURLY_RATE = float(context.user_data[SAVE_HOURLY_RATE])
            update.message.reply_text(
                f'Твоя ставка изменена с {DBHelper.per_hours_db(chat.id)} на '
                f'{HOURLY_RATE}р. ✅',
                reply_markup=buttons
            )
            salary = float(
                DBHelper.sku_db(chat.id) * UNIT_RATE_SKU +
                DBHelper.hours_db(chat.id) * HOURLY_RATE
            )
            DBHelper.hourly_rate_db(HOURLY_RATE, salary, chat.id)
            return ConversationHandler.END
        else:
            update.message.reply_text(message_error)
            return SAVE_HOURLY_RATE
    except ValueError:
        update.message.reply_text(message_error)
        return SAVE_HOURLY_RATE


def reset_counter(update, context):
    """Method to reset SKU and working hours."""
    chat = update.effective_chat
    buttons = ReplyKeyboardMarkup([['Да', 'Нет']], resize_keyboard=True)
    context.bot.send_message(
        chat_id=chat.id,
        text='Ты уверен, что хочешь сбросить все данные?',
        reply_markup=buttons
    )
    context.bot.send_message(
        chat_id=chat.id,
        text='Выбери "да" или "нет"'
    )
    return CNFRM_CNT_RESET


def confirm_reset(update, context):
    global SALARY, CNT_SKU, CNT_HOURS, NUMBER_OF_SHIFTS
    chat = update.effective_chat
    buttons = ReplyKeyboardRemove()
    if update.message.text.lower() == 'да':
        SALARY, CNT_SKU, CNT_HOURS, NUMBER_OF_SHIFTS = 0, 0, 0, 0
        DBHelper.edit_db(
            salary=SALARY,
            count_sku=CNT_SKU,
            count_hours=CNT_HOURS,
            count_shifts=NUMBER_OF_SHIFTS,
            chat_id=chat.id
        )
        context.bot.send_message(
            chat_id=chat.id,
            text='Данные успешно сброшены ✅',
            reply_markup=buttons
        )
        return ConversationHandler.END
    elif update.message.text.lower() == 'нет':
        context.bot.send_message(
            chat_id=chat.id,
            text='Данные остались без изменений ❌',
            reply_markup=buttons
        )
        return ConversationHandler.END
    else:
        context.bot.send_message(
            chat_id=chat.id,
            text='Нажми на кнопку "да" или "нет"'
        )
        return CNFRM_CNT_RESET


def cancel_hd(update, context):
    """Function to undo ConversationHandler."""
    update.message.reply_text('Отмена. Твои данные остались без изменений')
    return ConversationHandler.END


def main():
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('sku', data_for_that_day),
            CommandHandler('edit_sku', edit_sku),
            CommandHandler('edit_working_hours', edit_hourly_rate),
            CommandHandler('reset_counter', reset_counter),
        ],
        states={
            SKU: [
                MessageHandler(Filters.all, count_of_sku,
                               pass_user_data=True)
            ],
            WORKING_HOURS: [
                MessageHandler(Filters.all, count_of_hours,
                               pass_user_data=True)
            ],
            EDIT_SKU: [
                MessageHandler(Filters.all, new_rate_per_sku,
                               pass_user_data=True)
            ],
            SAVE_HOURLY_RATE: [
                MessageHandler(Filters.all, new_hourly_rate,
                               pass_user_data=True)
            ],
            CNFRM_CNT_RESET: [
                MessageHandler(Filters.all, confirm_reset, pass_user_data=True)
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_hd),
        ],
    )

    updater = Updater(TOKEN)

    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', help_description))
    updater.dispatcher.add_handler(CommandHandler('commands', bot_commands))
    updater.dispatcher.add_handler(CommandHandler('salary', salary))

    updater.start_polling()

    while True:
        logging.basicConfig(level=logging.INFO)
        logging.info('Раз в 10 минут и сообщение отправляется')
        time.sleep(600)


if __name__ == '__main__':
    main()
