import os, discord, json
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import tasks
from modules.setup.bot import bot
from modules.setup.logger import LOGGER
from modules.setup.data import DATA_DIR, get_guild_data

@tasks.loop(time=datetime.time(datetime.strptime('00:00','%H:%M')))
async def birthday_anouncements_task():
    LOGGER.debug('birthday_anouncements_task started.')
    for guild in bot.guilds:
        guild_data = get_guild_data(guild.id)
        if 'birthday_announcements_channel' in guild_data.keys():
            channel = guild.get_channel(guild_data['birthday_announcements_channel'])
            if 'birthday' in guild_data.keys():
                for user_id in guild_data['birthday'].keys():
                    user = bot.get_user(int(user_id))
                    if user:
                        if guild_data['birthday'][user_id]['announcements']:
                            date = guild_data['birthday'][user_id]['date']
                            today = datetime.today().strftime('%d/%m')
                            if date == today:
                                await channel.send(f'Joyeux anniversaire {user.mention}!')
        else:
            LOGGER.debug(f'No birthday_announcements_channel set for guild {guild.name} ({guild.id}).')
    LOGGER.debug('birthday_anouncements_task ended.')

@bot.slash_command(name='help',description='Displays this message.')
async def help(ctx:discord.ApplicationContext):
    """Displays this message."""
    command_name = 'help'
    LOGGER.debug(f'{ctx.author.name} used /{command_name}.')
    await ctx.send_response('test',ephemeral=True)

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
    birthday_anouncements_task.start()

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    bot.run(TOKEN)
    