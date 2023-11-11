import os, discord, json, sys
from argparse import ArgumentParser
from datetime import datetime
from dotenv import load_dotenv
from discord.ext import tasks, commands
from modules.setup.bot import bot
from modules.setup.logger import LOGGER
from modules.setup.data import DATA_DIR, get_guild_data

PARSER = ArgumentParser(description='BotMafieux for Discord.')
PARSER.add_argument('--guild_id',type=int,help='The guild ID.')
PARSER.add_argument('--channel_id',type=int,help='The channel ID.')
PARSER.add_argument('-r','--reload',action='store_true',help='Reload the bot.')
EXEC_ARGS = PARSER.parse_args()

@tasks.loop(time=datetime.time(datetime.strptime('00:00','%H:%M')))
async def birthday_anouncements_task():
    LOGGER.debug('birthday_anouncements_task started.')
    for guild in bot.guilds:
        guild_data = get_guild_data(guild.id)
        if 'birthday_announcements_channel' in guild_data['features']['birthday'].keys():
            channel = guild.get_channel(guild_data['features']['birthday']['birthday_announcements_channel'])
            if 'birthdays' in guild_data.keys():
                for user_id in guild_data['features']['birthday']['birthdays'].keys():
                    user = guild.get_member(int(user_id))
                    if user:
                        if guild_data['features']['birthday']['birthdays'][user_id]['announcements']:
                            date = guild_data['features']['birthday']['birthdays'][user_id]['date']
                            today = datetime.today().strftime('%d/%m')
                            if date == today:
                                await channel.send(f'Joyeux anniversaire {user.mention}!')
        else:
            LOGGER.debug(f'No birthday_announcements_channel set for guild {guild.name} ({guild.id}).')
    LOGGER.debug('birthday_anouncements_task ended.')

@bot.slash_command(name='help',description='Displays the help message.')
async def help(ctx:discord.ApplicationContext):
    """Displays this message."""
    command_name = 'help'
    LOGGER.debug(f'{ctx.author.name} used /{command_name}.')
    embed = discord.Embed(title='Help',description='List of commands and their descriptions.',color=discord.Color.from_rgb(171,0,219))
    embed.set_author(name=bot.user.name,icon_url=bot.user.avatar.url)
    for command in bot.commands:
        embed.add_field(name=command.name,value=command.description,inline=False)
    await ctx.send_response(embed=embed,ephemeral=True)

@bot.slash_command(name='reload',description='Reloads the bot.')
@commands.is_owner()
async def reload(ctx:discord.ApplicationContext):
    """Reloads the bot."""
    command_name = 'reload'
    guild = ctx.guild
    channel = ctx.channel
    LOGGER.debug(f'{ctx.author.name} used /{command_name}.')
    await ctx.send_response('Reloading...',ephemeral=True)
    args = [f'--guild_id={guild.id}',f'--channel_id={channel.id}','--reload']
    os.execl(sys.executable, sys.executable, __file__, *args)

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
    if EXEC_ARGS.guild_id and EXEC_ARGS.channel_id:
        guild = bot.get_guild(EXEC_ARGS.guild_id)
        channel = guild.get_channel_or_thread(EXEC_ARGS.channel_id)
        await channel.send(f'{bot.user.name} Bot reloaded!',silent=True)
    # Creates guild data files if they don't exist
    for guild in bot.guilds:
        guild_id = guild.id
        path = os.path.join(DATA_DIR, f'{guild_id}.json')
        if not os.path.exists(path):
            LOGGER.info(f'Creating data file for guild {guild_id}')
            with open(path, 'x') as f:
                json.dump({'features': {}}, f, indent=2)
    birthday_anouncements_task.start()

if __name__ == '__main__':
    LOGGER.debug(f'ARGS: {EXEC_ARGS}')
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    bot.run(TOKEN)
    