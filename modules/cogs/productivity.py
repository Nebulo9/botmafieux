import discord
from datetime import datetime
from discord.ext import commands, tasks
from discord import option
from typing import Union
from asyncio import sleep, create_task
from ..setup.logger import LOGGER
from ..setup.data import get_guild_data, save_guild_data, is_feature_enabled

TASKS = {}

async def send_reminder(cooldown:int,author:discord.Member,channel:discord.TextChannel,reminder_message:str=None):
        while True:
            await sleep(cooldown)
            LOGGER.debug(f'Sending productivity reminder to {author.name} in {channel.name} of {channel.guild.name}.')
            if reminder_message:
                await channel.send(f'{author.mention} {reminder_message}')
            else:
                await channel.send(f'{author.mention} You have not been active in this channel for a while. Please consider being more productive.')

class ProductivityCog(commands.Cog):
    
    def __init__(self,bot:discord.Bot) -> None:
        self.bot = bot
    
    @commands.slash_command(description='Configurate productivity reminder.')
    @option(name='channel',description='The channel to send productivity reminders in.',required=True)
    @option(name='enable',description='Enable or disable productivity reminders.',required=True)
    @option(name='days',description='Number of days to wait before sending a reminder if the user has not been active in the channel.',required=True,type=int)
    @option(name='custom_message',description='Custom message to send with the reminder.',required=False,type=str)
    @option(name='for_user',description='The user to configurate productivity reminders for.',required=False,type=discord.Member)
    async def productivity_config(self,ctx:discord.ApplicationContext, channel:Union[discord.TextChannel,discord.Thread], enable:bool, days:int, custom_message=None, for_user:discord.Member=None):
        """Configurate productivity reminder."""
        command_name = 'productivity_config'
        guild_id = ctx.guild.id
        guild_data = get_guild_data(guild_id)
        author = ctx.author
        if is_feature_enabled('productivity',data=guild_data):
            feature_data = guild_data['features']['productivity']
            if 'reminders' not in feature_data.keys():
                feature_data['reminders'] = dict()
            if str(author.id) not in feature_data['reminders'].keys():
                feature_data['reminders'][str(author.id)] = dict()
            if for_user:
                if author.guild_permissions.administrator:
                    user_data = feature_data['reminders'][str(for_user.id)]
                    LOGGER.debug(f'{author.name} used /{command_name} {channel.mention} {for_user.name}.')
                    user_data['channel'] = channel.id
                    user_data['enabled'] = enable
                    user_data['cooldown'] = days#*60*60*24
                    user_data['next_reminder'] = datetime.now().timestamp() + user_data['cooldown']
                    user_data['custom_message'] = custom_message
                    save_guild_data(guild_id, guild_data)
                    # create a task for the user
                    if for_user.id in TASKS.keys():
                        TASKS[str(for_user.id)].cancel()
                    TASKS[str(for_user.id)] = create_task(send_reminder(user_data['cooldown'],for_user,channel,user_data['custom_message']))
                    LOGGER.debug(f'{author.name} set up productivity reminders for {for_user.name}.')
                    await ctx.send_response(f'Productivity reminders for {for_user.name} have been set to {channel.mention}.',ephemeral=True)
                else:
                    LOGGER.debug(f'{author.name} tried to use /{command_name} {channel.mention} {for_user.name} but is not an administrator.')
                    await ctx.send_response('You must be an administrator to run the command with "for_user".',ephemeral=True)
            else:
                LOGGER.debug(f'{author.name} used /{command_name} {channel.mention}.')
                user_data = feature_data['reminders'][str(author.id)]
                user_data['channel'] = channel.id
                user_data['enabled'] = enable
                user_data['cooldown'] = days#*60*60*24
                user_data['next_reminder'] = datetime.now().timestamp() + user_data['cooldown']
                user_data['custom_message'] = custom_message
                save_guild_data(guild_id, guild_data)
                # create a task for the user
                if str(author.id) in TASKS.keys():
                    TASKS[str(author.id)].cancel()
                TASKS[str(author.id)] = create_task(send_reminder(user_data['cooldown'],author,channel,user_data['custom_message']))
                LOGGER.debug(f'{author.name} set up productivity reminders for {author.name}.')
                await ctx.send_response(f'Productivity reminders for {author.name} have been set to {channel.mention}.',ephemeral=True)
        else:
            LOGGER.debug(f'{author.name} tried to use /{command_name} {channel.mention} but the productivity feature is not enabled.')
            await ctx.send_response('The productivity feature is not enabled.',ephemeral=True)
    
    @commands.Cog.listener()
    async def on_message(self,message:discord.Message):
        author = message.author
        if author.id != self.bot.user.id:
            guild_id = message.guild.id
            guild_data = get_guild_data(guild_id)
            if is_feature_enabled('productivity',data=guild_data):
                channel = message.channel
                feature_data = guild_data['features']['productivity']
                if 'reminders' in feature_data.keys():
                    if str(author.id) in feature_data['reminders'].keys(): # If a user sat up its reminders
                        user_data = feature_data['reminders'][str(author.id)]
                        if user_data['enabled']: # If reminders are enabled for this user
                            reminder_channel_id = user_data['channel']
                            if channel.id == reminder_channel_id:
                                user_data['next_reminder'] = datetime.now().timestamp() + user_data['cooldown']
                                save_guild_data(guild_id, guild_data)
                                if author.id in TASKS.keys():
                                    TASKS[str(author.id)].cancel()
                                TASKS[str(author.id)] = create_task(send_reminder(user_data['cooldown'],author,channel,user_data['custom_message']))
                                LOGGER.debug(f'{author.name} sent a message in {channel.name} and reminders are set up in {reminder_channel_id}.')
                            else:
                                LOGGER.debug(f'{author.name} sent a message in {channel.name} but reminders are set up in {reminder_channel_id}.')

    
    