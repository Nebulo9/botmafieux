import discord
from datetime import datetime
from discord.ext import commands, tasks
from discord import option
from typing import Union, Optional
from asyncio import sleep, create_task
from ..setup.logger import LOGGER
from ..setup import db

TASKS = {}

async def send_reminder(cooldown:int,author:discord.Member,channel:discord.TextChannel,reminder_message:str):
        while True:
            await sleep(cooldown)
            LOGGER.debug(f'Sending productivity reminder to {author.name} in {channel.name} of {channel.guild.name}.')
            message = reminder_message.replace('{user}',author.mention)
            await channel.send(message)

class ProductivityCog(commands.Cog):
    
    def __init__(self,bot:discord.Bot) -> None:
        self.bot = bot
    
    @commands.slash_command(description='Configurate productivity reminder.')
    @option(name='channel',description='The channel to send productivity reminders in.',required=True)
    @option(name='enable',description='Enable or disable productivity reminders.',required=True)
    @option(name='days',description='Number of days to wait before sending a reminder if the user has not been active in the channel.',required=True,type=int)
    @option(name='custom_message',description='Custom message to send with the reminder.',required=False,type=str)
    @option(name='for_user',description='The user to configurate productivity reminders for.',required=False,type=discord.Member)
    async def productivity_set(self,ctx:discord.ApplicationContext, channel:Union[discord.TextChannel,discord.Thread], enable:bool, days:int, custom_message=None, for_user:discord.Member=None):
        """Configurate productivity reminder."""
        command_name = 'productivity_set'
        guild_id = ctx.guild.id
        author = ctx.author
        productivity_settings = db.select('productivity_settings',f'guild_id = {guild_id}')
        if productivity_settings:
            if productivity_settings['is_enabled']:
                if for_user:
                    if author.guild_permissions.administrator:
                        user_data = db.select('guild_user_productivity',f'guild_id = {guild_id} AND user_id = {for_user.id}')
                        cooldown = days*60*60*24
                        next_reminder = int(datetime.now().timestamp() + cooldown)
                        if user_data:
                            # Update user data
                            if custom_message:
                                db.update('guild_user_productivity',f'guild_id = {guild_id} AND user_id = {for_user.id}',channel_id=channel.id,cooldown=cooldown,next_reminder=next_reminder,reminder_message=custom_message,is_enabled=enable)
                                LOGGER.debug(f'{author.name} used /{command_name} {channel.mention} {enable} {days} {custom_message} for {for_user.name}.')
                                await ctx.send_response(f'Productivity reminders for {for_user.name} have been set to {channel.mention}.',ephemeral=True)
                            else:
                                db.update('guild_user_productivity',f'guild_id = {guild_id} AND user_id = {for_user.id}',channel_id=channel.id,cooldown=cooldown,next_reminder=next_reminder,is_enabled=enable)
                                LOGGER.debug(f'{author.name} used /{command_name} {channel.mention} {enable} {days} for {for_user.name}.')
                                await ctx.send_response(f'Productivity reminders for {for_user.name} have been set to {channel.mention}.',ephemeral=True)
                        else:
                            # Create user data
                            if custom_message:
                                db.insert('guild_user_productivity',guild_id=guild_id,user_id=for_user.id,channel_id=channel.id,cooldown=cooldown,next_reminder=next_reminder,reminder_message=custom_message,is_enabled=enable)
                                LOGGER.debug(f'{author.name} used /{command_name} {channel.mention} {enable} {days} {custom_message} for {for_user.name}.')
                                await ctx.send_response(f'Productivity reminders for {for_user.name} have been set to {channel.mention}.',ephemeral=True)
                            else:
                                db.insert('guild_user_productivity',guild_id=guild_id,user_id=for_user.id,channel_id=channel.id,cooldown=cooldown,next_reminder=next_reminder,is_enabled=enable)
                                LOGGER.debug(f'{author.name} used /{command_name} {channel.mention} {enable} {days} for {for_user.name}.')
                                await ctx.send_response(f'Productivity reminders for {for_user.name} have been set to {channel.mention}.',ephemeral=True)
                            user_data = db.select('guild_user_productivity',f'guild_id = {guild_id} AND user_id = {for_user.id}')
                        if str(for_user.id) in TASKS.keys():
                            TASKS[str(for_user.id)].cancel()
                        TASKS[str(for_user.id)] = create_task(send_reminder(cooldown,for_user,channel,user_data['reminder_message']))
                    else:
                        LOGGER.debug(f'{author.name} tried to use /{command_name} {channel.mention} {enable} {days} {custom_message} for {for_user.name} but is not an administrator.')
                        await ctx.send_response('You must be an administrator to run the command with "for_user".',ephemeral=True)
                else:
                    user_data = db.select('guild_user_productivity',f'guild_id = {guild_id} AND user_id = {author.id}')
                    cooldown = days*60*60*24
                    next_reminder = int(datetime.now().timestamp() + cooldown)
                    if user_data:
                        # Update user data
                        if custom_message:
                            db.update('guild_user_productivity',f'guild_id = {guild_id} AND user_id = {author.id}',channel_id=channel.id,cooldown=cooldown,next_reminder=next_reminder,reminder_message=custom_message,is_enabled=enable)
                            LOGGER.debug(f'{author.name} used /{command_name} {channel.mention} {enable} {days} {custom_message}.')
                            await ctx.send_response(f'Productivity reminders for {author.name} have been set to {channel.mention}.',ephemeral=True)
                        else:
                            db.update('guild_user_productivity',f'guild_id = {guild_id} AND user_id = {author.id}',channel_id=channel.id,cooldown=cooldown,next_reminder=next_reminder,is_enabled=enable)
                            LOGGER.debug(f'{author.name} used /{command_name} {channel.mention} {enable} {days}.')
                            await ctx.send_response(f'Productivity reminders for {author.name} have been set to {channel.mention}.',ephemeral=True)
                    else:
                        # Create user data
                        if custom_message:
                            db.insert('guild_user_productivity',guild_id=guild_id,user_id=author.id,channel_id=channel.id,cooldown=cooldown,next_reminder=next_reminder,reminder_message=custom_message,is_enabled=enable)
                            LOGGER.debug(f'{author.name} used /{command_name} {channel.mention} {enable} {days} {custom_message}.')
                            await ctx.send_response(f'Productivity reminders for {author.name} have been set to {channel.mention}.',ephemeral=True)
                        else:
                            db.insert('guild_user_productivity',guild_id=guild_id,user_id=author.id,channel_id=channel.id,cooldown=cooldown,next_reminder=next_reminder,is_enabled=enable)
                            LOGGER.debug(f'{author.name} used /{command_name} {channel.mention} {enable} {days}.')
                            await ctx.send_response(f'Productivity reminders for {author.name} have been set to {channel.mention}.',ephemeral=True)
                        user_data = db.select('guild_user_productivity',f'guild_id = {guild_id} AND user_id = {author.id}')
                    if str(author.id) in TASKS.keys():
                        TASKS[str(author.id)].cancel()
                    TASKS[str(author.id)] = create_task(send_reminder(cooldown,author,channel,user_data['reminder_message']))
            else:
                LOGGER.debug(f'{author.name} tried to use /{command_name} {channel.mention} {enable} {days} {custom_message} but the productivity feature is not enabled.')
                await ctx.send_response('The productivity feature is not enabled.',ephemeral=True)
        else:
            LOGGER.debug(f'{author.name} tried to use /{command_name} {channel.mention} {enable} {days} {custom_message} but no productivity settings were found.')
            await ctx.send_response('No productivity settings were found.',ephemeral=True)
    
    @commands.slash_command(description='Enable or disable productivity reminders on the server.')
    @option(name='enable',description='Enable or disable productivity reminders.',required=True)
    async def productivity_config(self,ctx:discord.ApplicationContext, enable:bool):
        """Enable or disable productivity reminders on the server."""
        command_name = 'productivity_config'
        guild_id = ctx.guild.id
        author = ctx.author
        productivity_settings = db.select('productivity_settings',f'guild_id = {guild_id}')
        if productivity_settings:
            # Update guild productivity settings
            if author.guild_permissions.administrator:
                LOGGER.debug(f'{author.name} used /{command_name} {enable}.')
                db.update('productivity_settings',f'guild_id = {guild_id}',is_enabled=enable)
                await ctx.send_response(f'Productivity reminders have been {"enabled" if enable else "disabled"}.',ephemeral=True)
            else:
                LOGGER.debug(f'{author.name} tried to use /{command_name} {enable} but is not an administrator.')
                await ctx.send_response('You must be an administrator to run this command.',ephemeral=True)
        else:
            # Create guild productivity settings
            if author.guild_permissions.administrator:
                LOGGER.debug(f'{author.name} used /{command_name} {enable}.')
                db.insert('productivity_settings',guild_id=guild_id,is_enabled=enable)
                await ctx.send_response(f'Productivity reminders have been {"enabled" if enable else "disabled"}.',ephemeral=True)
            else:
                LOGGER.debug(f'{author.name} tried to use /{command_name} {enable} but is not an administrator.')
                await ctx.send_response('You must be an administrator to run this command.',ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self,message:discord.Message):
        author = message.author
        if author.id != self.bot.user.id: # Ignore messages from the bot
            guild_id = message.guild.id
            productivity_settings = db.select('productivity_settings',f'guild_id = {guild_id}')
            if productivity_settings:
                if productivity_settings['is_enabled']:
                    user_productivity_data = db.select('guild_user_productivity',f'user_id = {author.id} AND guild_id = {guild_id}')
                    if user_productivity_data:
                        if user_productivity_data['is_enabled']:
                            next_reminder = int(datetime.now().timestamp() + user_productivity_data['cooldown'])
                            db.update('guild_user_productivity',f'user_id = {author.id} AND guild_id = {guild_id}',next_reminder=next_reminder)
                            if str(author.id) in TASKS.keys():
                                TASKS[str(author.id)].cancel()
                            TASKS[str(author.id)] = create_task(send_reminder(user_productivity_data['cooldown'],author,message.channel,user_productivity_data['reminder_message']))

    
    