import os, discord, logging, re, json
from dotenv import load_dotenv
from discord import option
from typing import Union
from discord.ext import tasks
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s: %(name)s: %(message)s')
LOGGER = logging.getLogger('botmafieux')
LOGGER.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='botmafieux.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
LOGGER.addHandler(handler)

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.members = True
bot_intents.presences = True
bot_intents.guilds = True
bot_intents.reactions = True

bot = discord.Bot(command_prefix='$', intents=bot_intents)

DATA_DIR = 'data/'

def get_guild_data(guild_id:int):
    """Reads and returns the dictionary of guild data from the guild's JSON data file."""
    path = os.path.join(DATA_DIR, f'{guild_id}.json')
    with open(path, 'r') as f:
        return json.load(f)

def save_guild_data(guild_id:int, data):
    """Saves the dictionary of guild data to the guild's JSON data file."""
    path = os.path.join(DATA_DIR, f'{guild_id}.json')
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

@bot.slash_command()
async def test(ctx:discord.ApplicationContext):
    """Test description"""
    user = ctx.author
    LOGGER.debug(f'{user.name} used /test.')
    await ctx.send_response('test',ephemeral=True)


@tasks.loop(time=datetime.time(datetime.strptime('00:00','%H:%M')))
async def test_loop():
    LOGGER.debug('test_loop')

@bot.slash_command(description='Sets birthday date. Must be in DAY/MONTH format.')
@option(name='date',description='Birthday date.',required=True)
@option(name='for_user',description='The user to set the birthday date for.',required=False,type=discord.Member)
async def birthday_set(ctx:discord.ApplicationContext, date:str, for_user:discord.Member):
    """Sets birthday date. Must be in DAY/MONTH format."""
    command_name = 'birthday_set'
    guild_id = ctx.guild.id
    guild_data = get_guild_data(guild_id)
    author = ctx.author
    if re.match(r'\d{2}\/\d{2}',date): # Check if date is in DAY/MONTH format
        if for_user:
            if author.guild_permissions.administrator: # Check if author is an administrator in case they want to set the birthday for another user
                LOGGER.debug(f'{author.name} used /{command_name} {date} for {for_user.name}.')
                if 'birthday' not in guild_data.keys():
                    guild_data['birthday'] = dict()
                if for_user.id not in guild_data['birthday'].keys():
                    guild_data['birthday'][str(for_user.id)] = dict()
                guild_data['birthday'][str(for_user.id)]['date'] = date
                if 'announcements' not in guild_data['birthday'][str(for_user.id)].keys():
                    guild_data['birthday'][str(for_user.id)]['announcements'] = True
                
                save_guild_data(guild_id, guild_data)
                await ctx.send_response(f'Birthday for {for_user.name} has been set to {date}.',ephemeral=True)
            else:
                LOGGER.debug(f'{author.name} tried to use /{command_name} {date} for {for_user.name} but is not an administrator.')
                await ctx.send_response('You must be an administrator to run the command with "for_user".',ephemeral=True)
        else:
            # Set birthday for author
            LOGGER.debug(f'{author.name} used /{command_name} {date}.')
            if 'birthday' not in guild_data.keys():
                guild_data['birthday'] = dict()
            if author.id not in guild_data['birthday'].keys():
                guild_data['birthday'][str(author.id)] = dict()
            guild_data['birthday'][str(author.id)]['date'] = date
            if 'announcements' not in guild_data['birthday'][str(author.id)].keys():
                guild_data['birthday'][str(author.id)]['announcements'] = True
            save_guild_data(guild_id, guild_data)
            
            # The status defines the human readable status of the announcements to be displayed in the response.
            announcements_status = 'are enabled' if guild_data['birthday'][str(author.id)]['announcements'] else 'aren\'t enabled'
            await ctx.send_response(f'Your birthday has been set to {date} and announcements {announcements_status}.',ephemeral=True)
    else:
        LOGGER.debug(f'{author.name} used /set_birthday {date} but the format is not correct.')
        await ctx.send_response('The date must is DAY/MONTH format.',ephemeral=True)

@bot.slash_command(description='Enable or disable birthday announcements.')
@option(name='enable',description='Enable birthday announcements.',required=True)
@option(name='for_user',description='The user to enable or disable birthday announcements for.',required=False)
async def birthday_announcements(ctx:discord.ApplicationContext, enable:bool, for_user:discord.Member):
    """Enable or disable birthday announcements."""
    command_name = 'birthday_announcements'
    guild_id = ctx.guild.id
    guild_data = get_guild_data(guild_id) or dict()
    author = ctx.author
    if for_user:
        if author.guild_permissions.administrator: # Check if author is an administrator in case they want to set the birthday for another user
            LOGGER.debug(f'{author.name} used /{command_name} {enable} for {for_user.name}.')
            guild_data['birthday'][str(for_user.id)]['announcements'] = enable
            save_guild_data(guild_id, guild_data)
            await ctx.send_response(f'Announcements for {for_user.name} are set to {enable}',ephemeral=True)
        else:
            LOGGER.debug(f'{author.name} tried to use /{command_name} {enable} for {for_user.name} but is not an administrator.')
            await ctx.send_response('You must be an administrator to run the command with "for_user".',ephemeral=True)
    else:
        LOGGER.debug(f'{author.name} used /{command_name} {enable}.')
        guild_data['birthday'][str(author.id)]['announcements'] = enable
        save_guild_data(guild_id, guild_data)
        await ctx.send_response(f'Your birthday announcements have been set to {enable}',ephemeral=True)

@bot.event
async def on_guild_join(guild:discord.Guild):
    LOGGER.info(f'Bot joined guild {guild.name} ({guild.id}).')
    path = os.path.join(DATA_DIR, f'{guild.id}.json')
    if not os.path.exists(path):
        LOGGER.info(f'Creating data file for guild {guild.id}')
        with open(path, 'x') as f:
            json.dump({}, f, indent=2)

@bot.event
async def on_guild_remove(guild:discord.Guild):
    LOGGER.info(f'Bot left guild {guild.name} ({guild.id}).')
    path = os.path.join(DATA_DIR, f'{guild.id}.json')
    if os.path.exists(path):
        LOGGER.info(f'Deleting data file for guild {guild.id}.')
        os.remove(path)

@bot.event
async def on_ready():
    LOGGER.info(f'{bot.user.name} has connected to Discord!')
    LOGGER.debug(f'Guilds: {bot.guilds}')
    # Creates guild data files if they don't exist
    for guild in bot.guilds:
        guild_id = guild.id
        path = os.path.join(DATA_DIR, f'{guild_id}.json')
        if not os.path.exists(path):
            LOGGER.info(f'Creating data file for guild {guild_id}')
            with open(path, 'x') as f:
                json.dump({}, f, indent=2)
    test_loop.start()

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    bot.run(TOKEN)
    