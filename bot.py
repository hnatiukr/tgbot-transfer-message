import config
from telethon import TelegramClient, sync, events

api_id = config.API_ID
api_hash = config.API_HASH
channel = config.CHANNEL

client = TelegramClient('anon', api_id, api_hash)
client.start()

# TODO: The functions bellow must be called continuously or periodically to check for new messages
# TODO: and collect information about reactions to them
# TODO: bot should work in real time


def get_participants_count():
    ''' Get count of participants channel '''
    get_participants = client.get_participants(channel)
    participants = len(get_participants)
    print(f'Participants in the channel: {participants}')
    # TODO: Use counter for calculation logic.
    return participants


get_participants_count()


def get_messages():
    ''' Get information about all messages in the channel '''
    messages = client.get_messages(channel, limit=None)
    return messages


def get_message_reactions():
    '''Get the number of clicked 'likes'  '''
    messages = get_messages()

    for message in messages:
        message_reactions_count = message.to_dict(
        )['reply_markup']['rows'][0]['buttons'][0]['text'][2:]

        # Check if there is at least one 'like'
        if message_reactions_count:
            # TODO: lwrite the logic of sending a message to another channel / group
            message_id = message.to_dict()['id']
            print(
                f'Message id: {message_id} has {message_reactions_count} reaction(s)')


get_message_reactions()


client.run_until_disconnected()
