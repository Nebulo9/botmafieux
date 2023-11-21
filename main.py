import os, discord, json, sys, random
import modules.setup.db as db
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
        birthday_settings = db.select('birthday_settings',f'guild_id = {guild.id}')
        if birthday_settings:
            if birthday_settings['is_enabled']:
                for user in guild.members:
                    user_productivity_data = db.select('guild_user_productivity',f'user_id = {user.id} AND guild_id = {guild.id}')
                    if user_productivity_data:
                        if user_productivity_data['is_enabled']:
                            user = guild.get_member(user.id)
                            if user:
                                birthday = user_productivity_data['birthday']
                                today = datetime.today().strftime('%d/%m')
                                if birthday == today:
                                    channel = guild.get_channel(user_productivity_data['channel_id'])
                                    if channel:
                                        message = user_productivity_data['birthday_message']
                                        if message:
                                            message = message.replace('{user}',user.mention)
                                            await channel.send(message)
                                    else:
                                        LOGGER.debug(f'Channel {user_productivity_data["channel_id"]} not found.')
                                else:
                                    LOGGER.debug(f'No birthday today for user {user.name} ({user.id}).')
                            else:
                                LOGGER.debug(f'User {user.name} ({user.id}) not found.')
                        else:
                            LOGGER.debug(f'User {user.name} ({user.id}) has birthday announcements disabled.')
                    else:
                        LOGGER.debug(f'No birthday data found for user {user.name} ({user.id}).')
        else:
            LOGGER.debug(f'No productivity settings found for guild {guild.name} ({guild.id}).')
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
async def on_member_join(member:discord.Member):
    if not member.bot:
        user_id = member.id
        user_name = member.name
        user_mention = member.mention
        db_user = db.select('global_user',f'WHERE user_id = {user_id}')
        if not db_user:
            db.insert('global_user',user_id=user_id,user_name=user_name,user_mention=user_mention)

@bot.event
async def on_raw_member_remove(payload:discord.RawMemberRemoveEvent):
    user = payload.user
    if not user.bot:
        user_id = user.id
        guild_id = payload.guild_id
        db.delete('guild_user_birthday',f'user_id = {user_id} AND guild_id = {guild_id}')
        db.delete('guild_user_productivity',f'user_id = {user_id} AND guild_id = {guild_id}')

@bot.event
async def on_guild_join(guild:discord.Guild):
    guild_id = guild.id
    guild_name = guild.name
    LOGGER.info(f'Bot joined guild {guild_name} ({guild_id}).')
    db.insert('guild',guild_id=guild_id)
    db.insert('birthday_settings',guild_id=guild_id,is_enabled=False,channel_id=random.choice(guild.text_channels).id)
    db.insert('productivity_settings',guild_id=guild_id,is_enabled=False)

@bot.event
async def on_guild_remove(guild:discord.Guild):
    guild_id = guild.id
    guild_name = guild.name
    LOGGER.info(f'Bot left guild {guild_name} ({guild_id}).')
    db.delete('birthday_settings',f'guild_id = {guild_id}')
    db.delete('productivity_settings',f'guild_id = {guild_id}')
    db.delete('guild',f'guild_id = {guild_id}')

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
        for user in guild.members:
            user_id = user.id
            db_user = db.select('global_user',f'user_id = {user_id}')
            if not db_user:
                db.insert('global_user',user_id=user_id,user_name=user.name,user_mention=user.mention)

        productivity_settings = db.select('productivity_settings',f'guild_id = {guild.id}')
        if productivity_settings:
            if productivity_settings['is_enabled']:
                for user in guild.members:
                    user_productivity_data = db.select('guild_user_productivity',f'user_id = {user.id} AND guild_id = {guild.id}')
                    if user_productivity_data:
                        if user_productivity_data['is_enabled']:
                            next_reminder = user_productivity_data['next_reminder']
                            if next_reminder > datetime.now().timestamp():
                                cooldown = next_reminder - datetime.now().timestamp()
                                channel = guild.get_channel(user_productivity_data['channel_id'])
                                reminder_message = user_productivity_data['reminder_message']
                                PRODUCTIVITY_TASKS[str(user.id)] = create_task(send_reminder(cooldown,user,channel,reminder_message))
                            else:
                                user_productivity_data['next_reminder'] = datetime.now().timestamp() + user_productivity_data['cooldown']
                                db.update('guild_user_productivity',f'user_id = {user.id} AND guild_id = {guild.id}',next_reminder=user_productivity_data['next_reminder'])
                                channel = guild.get_channel(user_productivity_data['channel_id'])
                                reminder_message = user_productivity_data['reminder_message']
                                PRODUCTIVITY_TASKS[str(user.id)] = create_task(send_reminder(user_productivity_data['cooldown'],user,channel,reminder_message))
        else:
            LOGGER.debug(f'No productivity settings found for guild {guild.name} ({guild.id}).')

if __name__ == '__main__':
    db.check_conn()
    result = db.select('token','token_name = \'discord\'','token_value')
    if result:
        TOKEN = result['token_value']
        bot.run(TOKEN)
    else:
        LOGGER.error('No token found.')
        sys.exit(1)
    