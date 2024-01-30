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

    # File not found: fill with default values
    except IOError:
        bot_vars = {
            'autoclean_user_ids': set(config['autoclean_user_ids']),
        }
        save()


# Utility functions
# ----------------------------------------------------------------------------------------------------------------------
def parse_id_set(args):

    if not args:
        raise Exception('you must specify at least one user id')

    return {int(x) for x in args}


async def get_member_nicks(guild: discord.Guild, ids):
    """Get user nicks / names from a list of user IDs"""
    nicks = []
    for x in set(ids):
        member = await guild.fetch_member(x)
        nicks.append(member.name if member.nick is None else member.nick)
    return nicks


# base commands
# ----------------------------------------------------------------------------------------------------------------------
async def cc_start(message, args: set):
    """Toggle on auto clean msgs"""
    bot_vars['autoclean_user_ids'] = bot_vars['autoclean_user_ids'] | args
    await message.channel.send('Enabled auto clean for `' + ', '.join(args) + '`')


async def cc_stop(message, args: set):
    """Toggle off auto clean"""
    bot_vars['autoclean_user_ids'] = bot_vars['autoclean_user_ids'] - args
    await message.channel.send('Disabled auto clean for `' + ', '.join(args) + '`')


async def cc_list(message):
    """Show auto clean list"""
    nicks = await get_member_nicks(message.guild, bot_vars['autoclean_user_ids'])
    await message.channel.send('Auto clean is enabled for `' + ', '.join(nicks) + '`')


# Command parser
# ----------------------------------------------------------------------------------------------------------------------
async def run_cmd(message, cmd, args):
    try:
        if cmd == 'start':
            await cc_start(message, parse_id_set(args))
        elif cmd == 'stop':
            await cc_stop(message, parse_id_set(args))
        elif cmd == 'list':
            await cc_list(message)

        # Unknown command
        else:
            await message.channel.send('Unknown command; Available are: come, leave, start, stop')
    except Exception as e:
        await message.channel.send(f'Failed to run command: {e}')


# ----------------------------------------------------------------------------------------------------------------------

load()

# Used in on_message to keep track of potential bot triggers
last_bot_trigger: discord.Message


@client.event
async def on_message(message):
    global last_bot_trigger

    # Bot call sign was used
    if message.content.startswith('cc') and message.author.id in config['admins']:
        # Parse cmd and args
        cmd_args = message.content.split()[1:]
        if len(cmd_args) > 0:
            await run_cmd(message, cmd_args[0], cmd_args[1:])

    # No call sign
    else:
        # Save a message if it looks like a bot trigger
        # (Bot replies do not start with these chars, so they won't overwrite)
        if message.content[0] in config['bot_triggers']:
            last_bot_trigger = message

        # If autoclean is on for the msg author
        if message.author.id in bot_vars['autoclean_user_ids']:
            await message.delete()

            # Also delete trigger message
            if last_bot_trigger is not None:
                await last_bot_trigger.delete()


client.run(config['token'])
