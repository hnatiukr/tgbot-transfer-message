import config
import logging
from uuid import uuid4
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start_cmd(update, context):
    user = update.effective_user

    if user:
        name = user.first_name
    else:
        name = 'anonym'

    # Welcome bot on command start
    reply_text = f'Hi, {name}!\n\n'
    update.message.reply_text(reply_text)


def help_cmd(update, context):
    update.message.reply_text("Use /start to test this bot.")


def error_handler(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def attach_button(update, context):
    counter = 0
    # button_content = f'👍 {counter}'
    button_content = '👍'
    keyboard = [[InlineKeyboardButton(button_content, callback_data=counter)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.channel_post.edit_reply_markup(reply_markup=reply_markup)


def button_handler(update, context):

    query = update.callback_query
    chat_id = query.message.chat_id
    user_id = update._effective_user.id
    message_id = query.message.message_id
    voted_users = context.user_data
    reposted_chats = context.chat_data
    members = context.bot.get_chat_members_count(chat_id=chat_id)
    prev_counter = query.message.reply_markup.inline_keyboard[0][0].callback_data

    counter = 0
    button_content = ''

    # Create an object to store users who have already liked the post
    # Check for matches. If it is already like - delete
    if message_id in voted_users:
        if user_id in voted_users[message_id]:
            voted_users[message_id].remove(user_id)
            counter = int(prev_counter) - 1
        else:
            voted_users[message_id].append(user_id)
            counter = int(prev_counter) + 1
    else:
        voted_users[message_id] = list()
        voted_users[message_id].append(user_id)
        counter = int(prev_counter) + 1

    # If no one likes - do not show the counter
    if counter < 1:
        button_content = '👍'
    else:
        button_content = f'👍 {counter}'

    # Update counter on the 'like' button
    keyboard = [[InlineKeyboardButton(button_content, callback_data=counter)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)

    # We repost to another channel if the data matches the condition
    # If the likes is equal to or more than half of subscribers, bot sends a message to another chat
    # Check for repost to chat
    if chat_id in reposted_chats:
        if message_id in reposted_chats[chat_id]:
            pass
        else:
            reposted_chats[chat_id].append(message_id)
            context.bot.send_message(
                chat_id=config.REPOST_CHANNEL, text=query.message.text)
    else:
        reposted_chats[chat_id] = list()
        reposted_chats[chat_id].append(message_id)
        context.bot.send_message(
            chat_id=config.REPOST_CHANNEL, text=query.message.text)

# if not chat_id in reposted_chats and counter >= members / 2:
#     reposted_chats[chat_id] = chat_id
#     context.bot.send_message(
#         chat_id=config.REPOST_CHANNEL, text=query.message.text)


def main():
    updater = Updater(config.TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start_cmd))
    dp.add_handler(CommandHandler('help', help_cmd))
    dp.add_handler(MessageHandler(
        Filters.all & (~Filters.command), attach_button))
    dp.add_handler(CallbackQueryHandler(button_handler))
    # updater.dispatcher.add_error_handler(error_handler)

    updater.start_polling()
    print(f'Bot is working now ...')
    updater.idle()


if __name__ == '__main__':
    main()
