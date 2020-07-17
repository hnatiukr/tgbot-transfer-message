# tgbot-transfer-message

**Transfer Message Bot** - this is a bot for automatically sending popular messages from one Telegram channel to another chat/channel.

**When to apply?** Imagine you have two channels. First - you use to post any messages. In the second you want to publish only the most interesting posts. In the first chat, a like button is attached to determine the interest of messages among subscribers. All "selected" messages will be automatically published in the second chat in turn.

## Installation 🛠

This API is tested with Python 3.7, Python 3.8. There is way to install the bot:

1. Clone the repository to a local or remote server:

   `git clone https://github.com/mort-gh/tgbot-transfer-message.git`

2. Create a new environment **.env** file in the root folder.
3. Add the environment variables with values to the created **.env** file:

```
    TOKEN=012356789:YOUR_BOT_TOKEN
    ROOT_CHAT=@channel_name 		// (or: ROOT_CHAT=-100123456789)
    REPOST_CHAT=@another_channel_name 	// (or: REPOST_CHAT=-100123456789)
    QUEUE_INTERVAL=3600			// optional
    COUNT=0				// optional
```

**TOKEN**: Token of your Bot for authorization in Telegram API. [How to get a token?](https://core.telegram.org/bots#6-botfather)

**ROOT_CHAT**: The unique ID of the main channel for publications. `@channel_name` - for the public channel, `-1000123456789` - for private channel. How to get ID of private channel - follow instructions [here](https://stackoverflow.com/questions/33858927/how-to-obtain-the-chat-id-of-a-private-telegram-channel/33862907#33862907) or [here](https://stackoverflow.com/questions/33858927/how-to-obtain-the-chat-id-of-a-private-telegram-channel/56546442#56546442).

> WARNING: do not ignore symbol `'@'` before `@channel_name` and `'-'`
> before ID `-1000123456789`!

**REPOST_CHAT**: This variable contains the name or ID of the channel where messages will be reposted. Follow the same instructions as in the **ROOT_CHAT**.

**QUEUE_INTERVAL**: The interval between sending messages. By default - `3600` **seconds**.

**COUNT**: Sets the number of `likes 👍` to forward messages. If `COUNT=0` (by default), the bot forwards the message when **half or more channel participants** vote for it.

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
