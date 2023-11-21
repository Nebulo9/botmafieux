import discord, re
from discord import option
from discord.ext import commands
from datetime import datetime
from ..setup.logger import LOGGER
from ..setup.data import get_guild_data, save_guild_data, is_feature_enabled
from ..setup import db

class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(description='Sets birthday date. Must be in DAY/MONTH format.')
    @option(name='date',description='Birthday date.',required=True)
    @option(name='announcements',description='Enable or disable birthday announcements.',required=True,type=bool)
    @option(name='message',description='The message to send when it is the user\'s birthday.',required=False)
    @option(name='for_user',description='The user to set the birthday date for.',required=False,type=discord.Member)
    async def birthday_set(self,ctx:discord.ApplicationContext, date:str,announcements:bool,message:str,for_user:discord.Member):
        """Sets birthday date. Must be in DAY/MONTH format."""
        command_name = 'birthday_set'
        guild_id = ctx.guild.id
        author = ctx.author
        birthday_settings = db.select('birthday_settings',f'guild_id = {guild_id}')
        if birthday_settings:
            if birthday_settings['is_enabled']:
                if for_user:
                    if author.guild_permissions.administrator:
                        if re.match(r'^\d{1,2}\/\d{1,2}$', date):
                            user_data = db.select('guild_user_birthday',f'guild_id = {guild_id} AND user_id = {for_user.id}')
                            if user_data:
                                # Update user data
                                if message:
                                    LOGGER.debug(f'{author.name} used /{command_name} {date} {announcements} {message} for {for_user.name}.')
                                    db.update('guild_user_birthday',f'guild_id = {guild_id} AND user_id = {for_user.id}',birthday=date,is_enabled=announcements,birthday_message=message)
                                else:
                                    LOGGER.debug(f'{author.name} used /{command_name} {date} {announcements} for {for_user.name}.')
                                    db.update('guild_user_birthday',f'guild_id = {guild_id} AND user_id = {for_user.id}',birthday=date,is_enabled=announcements)
                                await ctx.send_response(f'{for_user.name}\'s birthday has been set to {date}.',ephemeral=True)
                            else:
                                # Create user data
                                if message:
                                    LOGGER.debug(f'{author.name} used /{command_name} {date} {announcements} {message} for {for_user.name}.')
                                    db.insert('guild_user_birthday',guild_id=guild_id,user_id=for_user.id,birthday=date,is_enabled=announcements,birthday_message=message)
                                else:
                                    LOGGER.debug(f'{author.name} used /{command_name} {date} {announcements} for {for_user.name}.')
                                    db.insert('guild_user_birthday',guild_id=guild_id,user_id=for_user.id,birthday=date,is_enabled=announcements)
                                await ctx.send_response(f'{for_user.name}\'s birthday has been set to {date}.',ephemeral=True)
                        else:
                            LOGGER.debug(f'{author.name} tried to use /{command_name} {date} {announcements} {message} for {for_user.name} but the date format is invalid.')
                            await ctx.send_response('The date format must be DAY/MONTH.',ephemeral=True)
                    else:
                        LOGGER.debug(f'{author.name} tried to use /{command_name} {date} {announcements} {message} for {for_user.name} but is not an administrator.')
                        await ctx.send_response('You must be an administrator to run the command with "for_user".',ephemeral=True)
                else:
                    if re.match(r'^\d{1,2}\/\d{1,2}$', date):
                        user_data = db.select('guild_user_birthday',f'guild_id = {guild_id} AND user_id = {author.id}')
                        if user_data:
                            # Update user data
                            if message:
                                LOGGER.debug(f'{author.name} used /{command_name} {date} {announcements} {message}.')
                                db.update('guild_user_birthday',f'guild_id = {guild_id} AND user_id = {author.id}',birthday=date,is_enabled=announcements,birthday_message=message)
                            else:
                                LOGGER.debug(f'{author.name} used /{command_name} {date} {announcements}.')
                                db.update('guild_user_birthday',f'guild_id = {guild_id} AND user_id = {author.id}',birthday=date,is_enabled=announcements)
                            await ctx.send_response(f'Your birthday has been set to {date}.',ephemeral=True)
                        else:
                            # Create user data
                            if message:
                                LOGGER.debug(f'{author.name} used /{command_name} {date} {announcements} {message}.')
                                db.insert('guild_user_birthday',guild_id=guild_id,user_id=author.id,birthday=date,is_enabled=announcements,birthday_message=message)
                            else:
                                LOGGER.debug(f'{author.name} used /{command_name} {date} {announcements}.')
                                db.insert('guild_user_birthday',guild_id=guild_id,user_id=author.id,birthday=date,is_enabled=announcements)
                            await ctx.send_response(f'Your birthday has been set to {date}.',ephemeral=True)
                    else:
                        LOGGER.debug(f'{author.name} tried to use /{command_name} {date} {announcements} {message} but the date format is invalid.')
                        await ctx.send_response('The date format must be DAY/MONTH.',ephemeral=True)
            else:
                LOGGER.debug(f'{author.name} tried to use /{command_name} {date} {announcements} {message} but the birthday feature is not enabled.')
                await ctx.send_response('The birthday feature is not enabled.',ephemeral=True)
        else:
            LOGGER.debug(f'{author.name} tried to use /{command_name} {date} {announcements} {message} but the birthday feature is not enabled.')
            await ctx.send_response('The birthday feature is not enabled.',ephemeral=True)

    @commands.slash_command(description='Configurate birthday announcements.')
    @option(name='channel',description='The channel to send birthday announcements to.',required=True,type=discord.TextChannel)
    @option(name='enable',description='Enable or disable birthday announcements.',required=True,type=bool)
    async def birthday_config(self,ctx:discord.ApplicationContext, channel:discord.TextChannel,enable:bool):
        """Configurate birthday announcements."""
        command_name = 'birthday_config'
        guild_id = ctx.guild.id
        author = ctx.author
        birthday_settings = db.select('birthday_settings',f'guild_id = {guild_id}')
        if birthday_settings:
            # Update guild birthday settings
            if birthday_settings['is_enabled']:
                if author.guild_permissions.administrator:
                    LOGGER.debug(f'{author.name} used /{command_name} {channel.name} {enable}.')
                    db.update('birthday_settings',f'guild_id = {guild_id}',channel_id=channel.id,is_enabled=enable)
                    await ctx.send_response(f'Birthday announcements have been {"enabled" if enable else "disabled"} in {channel.mention}.',ephemeral=True)
                else:
                    LOGGER.debug(f'{author.name} tried to use /{command_name} {channel.name} {enable} but is not an administrator.')
                    await ctx.send_response('You must be an administrator to run this command.',ephemeral=True)
            else:
                LOGGER.debug(f'{author.name} tried to use /{command_name} {channel.name} {enable} but the birthday feature is not enabled.')
                await ctx.send_response('The birthday feature is not enabled.',ephemeral=True)
        else:
            # Create guild birthday settings
            if author.guild_permissions.administrator:
                LOGGER.debug(f'{author.name} used /{command_name} {channel.name} {enable}.')
                db.insert('birthday_settings',guild_id=guild_id,channel_id=channel.id,is_enabled=enable)
                await ctx.send_response(f'Birthday announcements have been {"enabled" if enable else "disabled"} in {channel.mention}.',ephemeral=True)
            else:
                LOGGER.debug(f'{author.name} tried to use /{command_name} {channel.name} {enable} but is not an administrator.')
                await ctx.send_response('You must be an administrator to run this command.',ephemeral=True)
            

