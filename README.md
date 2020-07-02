# tgbot-transfer-message

**Transfer Message Bot** is used to automatically send popular messages from one chat to another.

## Installation

To install the bot and run using [Docker](https://www.docker.com/), enter in the terminal: `docker-compose up`

## Usage

In the main chat, a Like  `👍`  button with a counter will be attached to each published message. If the number of likes is equal to or more than half the number of subscribers, the message becomes popular and gets queued for publication in another chat. Popular posts are published no more than once per hour. Using the bot, you can track which messages have been approved by the community and sent for forwarding.
