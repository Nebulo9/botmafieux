import os, discord, json, sys
from argparse import ArgumentParser
from datetime import datetime
from asyncio import create_task
from dotenv import load_dotenv
from discord import option
from discord.ext import tasks, commands
from modules.setup.bot import bot, reload_feature
from modules.setup.logger import LOGGER
from modules.setup.data import get_guild_data, create_guild_data, delete_guild_data, save_guild_data
from modules.cogs.productivity import TASKS as PRODUCTIVITY_TASKS, send_reminder

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
@option(name='feature',description='The feature to reload.',required=True,choices=['birthday','productivity'])
@commands.is_owner()
async def reload(ctx:discord.ApplicationContext, feature:str):
    """Reloads the bot."""
    command_name = 'reload'
    guild = ctx.guild
    channel = ctx.channel
    LOGGER.debug(f'{ctx.author.name} used /{command_name} {feature}.')
    try:
        reload_feature(feature)
        await ctx.send_response(f'{feature} reloaded!',ephemeral=True)
    except Exception as e:
        LOGGER.error(f'Error reloading feature {feature}: {e}')
        await ctx.send_response(f'Error reloading feature {feature}: {e}',ephemeral=True)


@bot.event
async def on_guild_join(guild:discord.Guild):
    guild_id = guild.id
    guild_name = guild.name
    LOGGER.info(f'Bot joined guild {guild_name} ({guild_id}).')
    create_guild_data(guild_id)

@bot.event
async def on_guild_remove(guild:discord.Guild):
    guild_id = guild.id
    guild_name = guild.name
    LOGGER.info(f'Bot left guild {guild_name} ({guild_id}).')
    delete_guild_data(guild_id)

@bot.event
async def on_ready():
    LOGGER.info(f'{bot.user.name} has connected to Discord!')
    LOGGER.debug(f'Guilds: {bot.guilds}')
    if EXEC_ARGS.reload and EXEC_ARGS.guild_id and EXEC_ARGS.channel_id:
        guild = bot.get_guild(EXEC_ARGS.guild_id)
        channel = guild.get_channel_or_thread(EXEC_ARGS.channel_id)
        await channel.send(f'{bot.user.name} Bot reloaded!',silent=True)
    birthday_anouncements_task.start()
    for guild in bot.guilds:
        guild_data = get_guild_data(guild.id)
        if 'features' in guild_data.keys():
            if 'productivity' in guild_data['features'].keys():
                if 'reminders' in guild_data['features']['productivity'].keys():
                    for user_id in guild_data['features']['productivity']['reminders'].keys():
                        user_data = guild_data['features']['productivity']['reminders'][user_id]
                        if user_data['enabled']:
                            next_reminder = user_data['next_reminder']
                            if next_reminder > datetime.now().timestamp():
                                cooldown = next_reminder - datetime.now().timestamp()
                                user = guild.get_member(int(user_id))
                                channel = guild.get_channel(user_data['channel'])
                                custom_message = user_data['custom_message']
                                PRODUCTIVITY_TASKS[user_id] = create_task(send_reminder(cooldown,user,channel,custom_message))
                            else:
                                user_data['next_reminder'] = datetime.now().timestamp() + user_data['cooldown']
                                save_guild_data(guild.id, guild_data)
                                user = guild.get_member(int(user_id))
                                channel = guild.get_channel(user_data['channel'])
                                custom_message = user_data['custom_message']
                                PRODUCTIVITY_TASKS[user_id] = create_task(send_reminder(user_data['cooldown'],user,channel,custom_message))

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    bot.run(TOKEN)
    