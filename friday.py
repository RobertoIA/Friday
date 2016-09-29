from os import environ
from time import sleep
from subprocess import call
from slackclient import SlackClient


def parse(msg, at_bot):
    """Identifies and retrieves messages directed at the bot.

    msg: a raw message retrieved by rtm_read()
    bot_at: bot mention, i.e. '<@U2H16C0KD>'

    command: message content if directed at the bot, None otherwise.
    channel: channel the message was found on, if directed at the bot.
    user: user that sent the message.
    """

    if msg:
        msg = msg[0]
        if msg and 'text' in msg and at_bot in msg['text']:
            command = msg['text'].split(at_bot)[1].strip().lower()
            command = command[1:] if command.startswith(':') else command
            channel = msg['channel']
            user = msg['user']
            return command, channel, user
    return None, None, None


def execute(client, user, command, channel):
    """Executes a command.

    client: connected Slack client.
    user: user that sent the command.
    command: command to execute.
    channel: channel the command was sent to.
    """

    print '[INFO] Received command \'%s\' from %s @ %s.' % (
        command, user, channel)

    if command.startswith('apaga'):
        client.api_call(
            'chat.postMessage',
            channel=channel,
            text='Buen intento %s' % user,
            as_user=True)

    else:
        client.api_call(
            'chat.postMessage',
            channel=channel,
            text='No entiendo, %s' % user,
            as_user=True)


def loop(client, bot_id):
    """Main bot loop.

    client: connected slack client.
    bot_id: id associated with the bot.
    """

    bot_at = '<@%s>' % bot_id
    while True:
        command, channel, user = parse(client.rtm_read(), bot_at)
        user = get_name(client, user)
        if command and channel: execute(client, user, command, channel)
        sleep(.5)


def get_name(client, id):
    """Retrieves the username associated with an id.

    client: connected Slack client.
    id: id to retrieve."""

    user_call = client.api_call('users.list')
    if user_call.get('ok'):
        for user in user_call.get('members'):
            if user.get('id') == id: return user.get('name')


def get_id(client, name):
    """Retrieves the id associated with a username.

    client: connected Slack client.
    name: username to retrieve.
    """

    user_call = client.api_call('users.list')
    if user_call.get('ok'):
        for user in user_call.get('members'):
            if user.get('name') == name: return user.get('id')
    return


def bot(token):
    """Bot initialization.
    Connects to Slack, retrieves the bot id and starts the main loop.

    token: Slack API token.
    """

    client = SlackClient(token)
    if client.rtm_connect():
        print '[INFO] Connected'
        bot_id = get_id(client, 'friday')
        if bot_id: loop(client, bot_id)
        else: print '[ERROR] Unable to find bot id'
    else: print '[ERROR] Unable to find bot'


if __name__ == '__main__':
    token = environ.get('SLACK_TOKEN', None)

    if token: bot(token)
    else: print '[ERROR] Missing API Token'
