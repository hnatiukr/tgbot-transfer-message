import config
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start_cmd(update, context):
    user = update.effective_user
    name = user.user.first_name if user else 'anonym'

    # Welcome bot on command start
    reply_text = f'Hi, {name}!\n\nWith this bot, you can automatically forward the most popular chat messages to other chats.'
    update.message.reply_text(reply_text)


def help_cmd(update, context):
    update.message.reply_text('Use /start to test this bot.')


def error_handler(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def attach_button(update, context):
    ''' Attach a button to each message '''

    root_chat_id = config.MAIN_CHAT
    current_chat_id = update.channel_post.chat.id

    counter = 0
    button_content = '👍'

    keyboard = [[InlineKeyboardButton(button_content, callback_data=counter)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # 'Like' button is attached only in the root chat to which the bot is connected
    if str(current_chat_id) == str(root_chat_id):
        update.channel_post.edit_reply_markup(reply_markup=reply_markup)


def button_handler(update, context):
    ''' "Like" button click handler '''

    # Check the status of the button counter, user identity. Change the value of the button.
    counter = is_post_liked(update, context)

    # Check for an empty value
    button = button = '👍' if counter < 1 else f'👍 {counter}'

    # Update button value. Send new data
    update_counter_value(update, context, button, counter)

    # If the message is popular, we send it to your favorite chats. False positive check
    is_message_forward(update, context, counter)


def is_post_liked(update, context):
    ''' Create an object to store users who have already liked the post
    Check for matches. If it is already like - delete '''

    query = update.callback_query
    user_id = update._effective_user.id
    message_id = query.message.message_id
    voted_users = context.user_data
    prev_counter = query.message.reply_markup.inline_keyboard[0][0].callback_data

    counter = 0

    # If this message has already voted:
    if message_id in voted_users:
        # If the current user has already voted, delete the vote:
        if user_id in voted_users[message_id]:
            voted_users[message_id].remove(user_id)
            counter = int(prev_counter) - 1
        # Else -  add vote
        else:
            voted_users[message_id].append(user_id)
            counter = int(prev_counter) + 1
    # If you have not yet voted for this message, create a list for votes and add vote:
    else:
        voted_users[message_id] = list()
        voted_users[message_id].append(user_id)
        counter = int(prev_counter) + 1

    return counter


def update_counter_value(update, context, button, counter):
    ''' Update counter on the 'like' button '''

    query = update.callback_query
    chat_id = config.MAIN_CHAT
    message_id = query.message.message_id

    keyboard = [[InlineKeyboardButton(button, callback_data=counter)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_reply_markup(
        chat_id=chat_id, message_id=message_id, reply_markup=reply_markup)


def is_message_forward(update, context, counter):
    ''' We repost to another channel if the data matches the condition (** 1/2 of members **)
    If the likes is equal to or more than half of subscribers, bot forward a message to another chat
    Check for repost to chat '''

    chat_id = config.MAIN_CHAT
    repost_to_chat = config.REPOST_CHAT
    query = update.callback_query
    message_id = query.message.message_id
    reposted_chats = context.chat_data

    members = context.bot.get_chat_members_count(chat_id=chat_id)

    # If the button is pressed by the required number of users (1/2 of members):
    if counter >= members / 2:
        # Chat identity check:
        if chat_id in reposted_chats:
            # If the current message has already reposted, do nothing
            if message_id in reposted_chats[chat_id]:
                pass
            # Else, remember the message and repost
            else:
                reposted_chats[chat_id].append(message_id)
                context.bot.forward_message(
                    chat_id=repost_to_chat,
                    from_chat_id=chat_id,
                    message_id=message_id,
                )
        # If the message is reposted for the first time from this chat, remember it and repost
        else:
            reposted_chats[chat_id] = list()
            reposted_chats[chat_id].append(message_id)
            context.bot.forward_message(
                chat_id=repost_to_chat,
                from_chat_id=chat_id,
                message_id=message_id,
            )


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
