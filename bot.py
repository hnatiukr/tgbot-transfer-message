import os
import logging
import datetime
import telegram.ext
from dotenv import load_dotenv
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler,
                          MessageHandler, Filters, PicklePersistence)
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TOKEN")
ROOT_CHAT = os.environ.get("ROOT_CHAT")
REPOST_CHAT = os.environ.get("REPOST_CHAT")
QUEUE_INTERVAL = int(os.environ.get("QUEUE_INTERVAL", 3600))
COUNT = int(os.environ.get("COUNT", 0))


def start_cmd(update, context):
    user = update.effective_user
    name = user.first_name if user else 'anonym'

    # Welcome bot on command start
    reply_text = f'''Hi, {name}!\n\n
    With this bot, you can automatically forward the most popular chat messages from channel to other chats.\n\n
    Before to start check your configuration settings:\n
    Channel for posts: {ROOT_CHAT}
    Channel for reposts: {REPOST_CHAT}
    Time interval between reposts (sec): {QUEUE_INTERVAL}
    Minimum number of likes (if 0 - half the channel’s subscribers): {COUNT}
    '''
    update.message.reply_text(reply_text)


def help_cmd(update, context):
    update.message.reply_text('Use /start to test this bot.')


def attach_button(update, context):
    ''' Attach a button to each message '''

    # Check for chat type:
    if update.channel_post:
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
    if COUNT != 0 and counter >= COUNT:
        queue_job(update, context, button, counter)
        # attach_timer_button(update, context, button, counter)
    else:
        members = context.bot.get_chat_members_count(chat_id=ROOT_CHAT)
        if counter >= members / 2:
            queue_job(update, context, button, counter)
            # attach_timer_button(update, context, button, counter)


def get_like_count(update, context):
    ''' Create an object to store users who have already liked the post
    Check for matches. If it is already like - delete '''

    user_data = context.user_data
    user_id = update._effective_user.id
    message_query = update.callback_query.message
    message_id = message_query.message_id
    prev_counter = message_query.reply_markup.inline_keyboard[0][0].callback_data

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

    message_id = update.callback_query.message.message_id
    keyboard = [[InlineKeyboardButton(button, callback_data=counter)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_reply_markup(
        chat_id=ROOT_CHAT, message_id=message_id, reply_markup=reply_markup)


def attach_timer_button(update, context, button, counter):
    ''' Attach a button to each popular message '''

    message_id = update.callback_query.message.message_id
    formated_time = get_scheduled_queue_time(context)
    button_timer = f'🔥 {formated_time}'
    url = f'https://t.me/{REPOST_CHAT[1:]}'

    # Attach timer - button for popular message and update counter on the 'like' button:
    keyboard = [[InlineKeyboardButton(button, callback_data=counter),
                 InlineKeyboardButton(button_timer, url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_reply_markup(
        chat_id=ROOT_CHAT, message_id=message_id, reply_markup=reply_markup)


def get_scheduled_queue_time(context):
    bot_data = context.bot_data
    waiting_time = len(bot_data['queue']) * QUEUE_INTERVAL
    datetime_now = datetime.datetime.now()
    post_time = datetime_now + datetime.timedelta(seconds=waiting_time)
    formated_time = post_time.strftime("%H:%M, %a")

    return formated_time


def queue_job(update, context, button, counter):
    ''' Remember the current message and add to the job queue '''

    message_id = update.callback_query.message.message_id
    chat_data = context.chat_data
    bot_data = context.bot_data

    # If there are no current chat entries:
    if ROOT_CHAT not in chat_data:
        chat_data[ROOT_CHAT] = []

    # Create queue if not exist:
    if 'queue' not in bot_data:
        bot_data['queue'] = []

    # If the current message has not already reposted, remember it and add to the queue:
    if message_id not in chat_data[ROOT_CHAT]:

        # Add a timer - button to messages that have not yet been in the queue:
        attach_timer_button(update, context, button, counter)

        # Save message data for publication in REPOST_CHAT:
        message_text = update.callback_query.message.text
        message_photo = update.callback_query.message.photo
        message_caption = update.callback_query.message.caption

        chat_data[ROOT_CHAT].append(message_id)
        bot_data['queue'].insert(0, {
            'message_id': message_id,
            'text': message_text,
            'photo': message_photo,
            'caption': message_caption
        })


def forward_message(context: telegram.ext.CallbackContext):
    ''' Bot forward a message to another chat from queue once an hour '''

    bot_data = context.job.context[0]

    # If the queue has not yet been created, exit the function:
    if 'queue' not in bot_data:
        return

    # If there are elements in the queue, forward the message:
    queue = bot_data['queue']

    if len(queue) > 0:
        message_data = queue.pop()

        # If the message doesn't contains photo, but only text or Youtube video:
        if not message_data['photo']:
            message_text = message_data['text']
            context.bot.send_message(
                chat_id=REPOST_CHAT,
                text=message_text,
                parse_mode=telegram.ParseMode.MARKDOWN
            )

        # If the message contains an photo and a caption:
        else:
            # Choose the photo with the highest quality, which is the last in the list of permissions:
            message_photo = message_data['photo'][-1]['file_id']
            message_caption = message_data['caption']
            context.bot.send_photo(
                chat_id=REPOST_CHAT,
                photo=message_photo,
                caption=message_caption,
            )


def main():
    my_persistence = PicklePersistence(filename='bot_data')
    updater = Updater(TOKEN, persistence=my_persistence, use_context=True)
    ud = updater.dispatcher
    ud.add_handler(CommandHandler('start', start_cmd))
    ud.add_handler(CommandHandler('help', help_cmd))
    ud.add_handler(MessageHandler(
        Filters.all & (~Filters.command) & Filters.chat(username=ROOT_CHAT), attach_button))
    ud.add_handler(CallbackQueryHandler(button_handler))

    j = updater.job_queue
    job_minute = j.run_repeating(
        forward_message,
        interval=QUEUE_INTERVAL,
        context=[ud.bot_data]
    )

    updater.start_polling()
    print(f'Bot is working now ...')
    updater.idle()


if __name__ == '__main__':
    main()
