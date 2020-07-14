# tgbot-transfer-message

**Transfer Message Bot** - this is a bot for automatically sending popular messages from one Telegram channel to another chat/channel.

Imagine you have two channels. First - you use to post any messages. In the second you want to publish only the most interesting posts. In the first chat, a like button is attached to determine the interest of messages among subscribers. All "selected" messages will be automatically published in the second chat in turn.

## Installation Bot 🛠

This API is tested with Python 3.7, Python 3.8. There is way to install the bot:

1. Clone the repository to a local or remote server:

   `git clone https://github.com/mort-gh/tgbot-transfer-message.git`

2. Create a new environment file **.env** in the root folder.
3. Add the following environment variables with values to the created **.env** file:

```
	TOKEN=012356789:YOUR_BOT_TOKEN
    ROOT_CHAT=@channel_name 			// (or: ROOT_CHAT=-0123456789)
    REPOST_CHAT=@another_channel_name 	// (or: REPOST_CHAT=-0123456789)
    QUEUE_INTERVAL=3600					// optional
    COUNT=0								// optional
```

**TOKEN**: Each bot is given a unique authentication token when it is created. The token looks something like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`. [BotFather](https://t.me/botfather) is the one bot to rule them all. It will help you create new bots and change settings for existing ones. Use the **/newbot** command to create a new bot. The BotFather will ask you for a name and username, then generate an authorization token for your new bot.

**ROOT_CHAT**: This variable contains the unique ID of the main channel for publications. The main chat can be used not only channels. For public channel - with a unique address like a `@channel_name` (look in the channel info), for private channel - with a unique ID like a `-1000123456789`.

How to get ID of private channel - follow instructions [here](https://stackoverflow.com/questions/33858927/how-to-obtain-the-chat-id-of-a-private-telegram-channel/33862907#33862907) or [here](https://stackoverflow.com/questions/33858927/how-to-obtain-the-chat-id-of-a-private-telegram-channel/56546442#56546442).

> WARNING: do not ignore symbol `'@'` before `@channel_name` and `'-'`
> before ID `-1000123456789`!

[How are private and public channels different?](https://telegram.org/faq_channels#q-how-are-public-and-private-channels-different)

**REPOST_CHAT**: This variable contains the name or ID of the channel where messages will be reposted. Follow the same instructions as in the **ROOT_CHAT**.

**QUEUE_INTERVAL**: So that the bot does not repost several messages in a row at once, it creates a queue and after a specified time interval checks for new messages. The interval is set in seconds. By default, the bot sends messages no more than once per hour - `3600` seconds.

**COUNT**: This variable is optional. It sets the number of “likes” for the message to become popular, and has been queued for repost. If the value is `0` (by default), the bot determines the message is popular when **half or more channel members** vote for it.

4. Install dependencies and download required libraries:

`pip3 install -r requirements.txt`

5. Add your bot to the administrators of **both channels**:

`Telegram App` -> `Channel info` -> `Administrators` -> `Add Administrator` -> `Chose Your Bot`

## Usage 💻

In the main channel, a Like `👍` button with a counter will be attached to each published message. If the number of likes is equal to `COUNT` value or more than half the number of subscribers, the message becomes popular and gets queued for publication in another chat. Popular posts are published no more than once per time in `QUEUE_INTERVAL`. Using the bot, you can track which messages most popular in the community to repost them into another chat.

1. To start the bot after installation, type in the terminal:

`python3 bot.by`

2. Press **Start** to launch the bot in the Telegram app

3. Post some test message to the main channel to see how it works.

4. Enjoy!

> To run using [Docker](https://www.docker.com/), enter in the terminal:
> `docker-compose up`
