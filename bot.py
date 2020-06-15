import config
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text("Hi! Write smth to publish")


def button(update, context):
    print(f' ********** UPDATE ********* {update}')
    query = update.callback_query
    chat_id = query.message.chat_id
    message_id = query.message.message_id
    # user_id = update.message.chat.id
    prev_counter = query.message.reply_markup.inline_keyboard[0][0].callback_data

    updated_counter = int(prev_counter) + 1

    if updated_counter > 0:
        button_content = f'👍 {updated_counter}'
    else:
        button_content = '👍'

    keyboard = [[InlineKeyboardButton(
        button_content, callback_data=updated_counter)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)


def help(update, context):
    update.message.reply_text("Use /start to test this bot.")


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def send_to_chat(update, context):
    chat_id = config.CHAT_ID
    button_content = '👍'

    keyboard = [[InlineKeyboardButton(
        button_content, callback_data=0)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=chat_id, text=update.message.text, photo=update.message.photo, parse_mode='Markdown', reply_markup=reply_markup)


def main():
    updater = Updater(config.TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(MessageHandler(
        Filters.all & (~Filters.command), send_to_chat))
    updater.dispatcher.add_error_handler(error)

    updater.start_polling()
    print(f'Bot is working now ...')
    updater.idle()


if __name__ == '__main__':
    main()
