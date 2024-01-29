import json
import pickle

import discord

intents = discord.Intents.none()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

bot_vars = {}
with open('secret.json', 'r') as f:
    config = json.load(f)


# persistence
# ----------------------------------------------------------------------------------------------------------------------
def save():
    with open('bot_vars.pickle', 'wb') as save_file:
        pickle.dump(bot_vars, save_file)
        save_file.close()


def load():
    global bot_vars
    try:
        with open('bot_vars.pickle', 'rb') as save_file:
            bot_vars = pickle.load(save_file)
            save_file.close()
    except IOError:
        bot_vars = {
            'admin_ids': set(config['admins']),
            'autoclean_user_ids': set(config['autoclean_user_ids']),
        }
        save()

# ----------------------------------------------------------------------------------------------------------------------


# base commands
# ----------------------------------------------------------------------------------------------------------------------

def parse_id_set(args):
    return {int(x) for x in args}


async def get_member_nicks(guild: discord.Guild, ids):
    nicks = []
    for x in set(ids):
        member = await guild.fetch_member(x)
        nicks.append(member.name if member.nick is None else member.nick)
    return nicks


async def py_start(message, args: set):
    """Toggle on auto clean msgs"""

    bot_vars['autoclean_user_ids'] = bot_vars['autoclean_user_ids'] | args
    nicks = await get_member_nicks(message.guild, bot_vars['autoclean_user_ids'])
    await message.channel.send('Autoclean is enabled for `' + ', '.join(nicks) + '`')


async def py_stop(message, args: set):
    """Toggle off auto clean"""

    if not args:
        raise Exception('you must specify at least one user id')

    bot_vars['autoclean_user_ids'] = bot_vars['autoclean_user_ids'] - args
    nicks = await get_member_nicks(message.guild, args)
    await message.channel.send('Autoclean was disabled for `' + ', '.join(nicks) + '`')


# ----------------------------------------------------------------------------------------------------------------------

async def run_cmd(message, cmd, args):
    try:
        if cmd == 'start':
            await py_start(message, parse_id_set(args))
        elif cmd == 'stop':
            await py_stop(message, parse_id_set(args))
        # Unknown command
        else:
            await message.channel.send('Unknown command; Available are: come, leave, start, stop')
    except Exception as e:
        await message.channel.send(f'Failed to run command: {e}')


# ----------------------------------------------------------------------------------------------------------------------

load()
# print('bot_vars pre-set to: ' + str(bot_vars))

# Used in on_message to keep track of potential bot triggers
last_bot_trigger: discord.Message


@client.event
async def on_message(message):
    global last_bot_trigger

    # Bot call sign was used
    if message.content.startswith('cc') and message.author.id in bot_vars['admin_ids']:
        # Parse cmd and args
        cmd_args = message.content.split()[1:]
        if len(cmd_args) > 0:
            await run_cmd(message, cmd_args[0], cmd_args[1:])

    # No call sign
    else:
        # Save a message if it looks like a bot trigger
        # (Bot replies do not start with these chars, so they won't overwrite)
        if message.content[0] in ['.', '!', '-']:
            last_bot_trigger = message

        # If autoclean is on for the msg author
        if message.author.id in bot_vars['autoclean_user_ids']:
            await message.delete()

            # Also delete trigger message
            if last_bot_trigger is not None:
                await last_bot_trigger.delete()


client.run(config['token'])
