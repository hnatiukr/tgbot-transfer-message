import config
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters, PicklePersistence


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start_cmd(update, context):
    user = update.effective_user
    name = user.first_name if user else 'anonym'

    # Welcome bot on command start
    reply_text = f'Hi, {name}!\n\nWith this bot, you can automatically forward the most popular chat messages to other chats.'
    update.message.reply_text(reply_text)


def help_cmd(update, context):
    update.message.reply_text('Use /start to test this bot.')


def error_handler(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def attach_button(update, context):
    ''' Attach a button to each message '''

    # Check for chat type (channel)
    if update.channel_post:
        root_chat_id = config.ROOT_CHAT
        current_chat_id = update.channel_post.chat.id

        # 'Like' button is attached only in the root chat to which the bot is connected
        if str(current_chat_id) == str(root_chat_id):
            counter = 0
            button_content = '👍'

            keyboard = [[InlineKeyboardButton(
                button_content, callback_data=counter)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.channel_post.edit_reply_markup(reply_markup=reply_markup)


def button_handler(update, context):
    ''' "Like" button click handler '''

    # Check the status of the button counter, user identity. Change the value of the button.
    counter = get_like_count(update, context)

    # Check for an empty value
    button = '👍' if counter < 1 else f'👍 {counter}'

    # Update button value. Send new data
    update_counter_value(update, context, button, counter)

    # If the message is popular, we send it to your favorite chats.
    # now: (1/2 of members)
    chat_id = config.ROOT_CHAT
    members = context.bot.get_chat_members_count(chat_id=chat_id)

    if counter >= members / 2:
        try_forward_message(update, context)


def get_like_count(update, context):
    ''' Create an object to store users who have already liked the post
    Check for matches. If it is already like - delete '''

    user_data = context.user_data
    user_id = update._effective_user.id
    message_id = update.callback_query.message.message_id
    prev_counter = update.callback_query.message.reply_markup.inline_keyboard[
        0][0].callback_data

    counter = 0

    # If this message has already voted:
    if message_id not in user_data:
        user_data[message_id] = []
    # If the current user has already voted, delete the vote:
    if user_id in user_data[message_id]:
        user_data[message_id].remove(user_id)
        counter = int(prev_counter) - 1
    # Else -  add vote
    else:
        user_data[message_id].append(user_id)
        counter = int(prev_counter) + 1

    return counter


def update_counter_value(update, context, button, counter):
    ''' Update counter on the 'like' button '''

    chat_id = config.ROOT_CHAT
    message_id = update.callback_query.message.message_id

    keyboard = [[InlineKeyboardButton(button, callback_data=counter)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)


def try_forward_message(update, context):
    ''' Bot forward a message to another chat '''

    chat_id = config.ROOT_CHAT
    message_id = update.callback_query.message.message_id
    chat_data = context.chat_data

    # If there are no current chat entries
    if chat_id not in chat_data:
        chat_data[chat_id] = []

    # If the current message has not already reposted, remember it and repost
    if message_id not in chat_data[chat_id]:
        chat_to_repost = config.REPOST_CHAT

        chat_data[chat_id].append(message_id)
        context.bot.forward_message(
            chat_id=chat_to_repost,
            from_chat_id=chat_id,
            message_id=message_id,
        )


def main():
    my_persistence = PicklePersistence(filename='bot_data')
    updater = Updater(
        config.TOKEN, persistence=my_persistence, use_context=True)
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
