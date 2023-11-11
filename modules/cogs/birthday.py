import discord, re
from discord import option
from discord.ext import commands
from ..setup.logger import LOGGER
from ..setup.data import get_guild_data, save_guild_data

class BirthdayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.slash_command(description='Sets birthday date. Must be in DAY/MONTH format.')
    @option(name='date',description='Birthday date.',required=True)
    @option(name='for_user',description='The user to set the birthday date for.',required=False,type=discord.Member)
    async def birthday_set(self,ctx:discord.ApplicationContext, date:str, for_user:discord.Member):
        """Sets birthday date. Must be in DAY/MONTH format."""
        command_name = 'birthday_set'
        guild_id = ctx.guild.id
        guild_data = get_guild_data(guild_id)
        author = ctx.author
        if re.match(r'\d{2}\/\d{2}',date): # Check if date is in DAY/MONTH format
            if for_user:
                if author.guild_permissions.administrator: # Check if author is an administrator in case they want to set the birthday for another user
                    LOGGER.debug(f'{author.name} used /{command_name} {date} for {for_user.name}.')
                    if 'birthday' not in guild_data['features'].keys():
                        guild_data['features']['birthday'] = dict()
                    if 'birthdays' not in guild_data['features']['birthday'].keys():
                        guild_data['features']['birthday']['birthdays'] = dict()
                    if str(for_user.id) not in guild_data['features']['birthday']['birthdays'].keys():
                        guild_data['features']['birthday'][str(for_user.id)] = dict()
                    guild_data['features']['birthday']['birthdays'][str(for_user.id)]['date'] = date
                    guild_data['features']['birthday']['birthdays'][str(for_user.id)]['announcements'] = True

                    save_guild_data(guild_id, guild_data)
                    await ctx.send_response(f'Birthday for {for_user.name} has been set to {date}.',ephemeral=True)
                else:
                    LOGGER.debug(f'{author.name} tried to use /{command_name} {date} for {for_user.name} but is not an administrator.')
                    await ctx.send_response('You must be an administrator to run the command with "for_user".',ephemeral=True)
            else:
                # Set birthday for author
                LOGGER.debug(f'{author.name} used /{command_name} {date}.')
                if 'birthday' not in guild_data['features'].keys():
                    guild_data['features']['birthday'] = dict()
                if 'birthdays' not in guild_data['features']['birthday'].keys():
                    guild_data['features']['birthday']['birthdays'] = dict()
                if author.id not in guild_data['features']['birthday']['birthdays'].keys():
                    guild_data['features']['birthday']['birthdays'][str(author.id)] = dict()
                guild_data['features']['birthday']['birthdays'][str(author.id)]['date'] = date
                guild_data['features']['birthday']['birthdays'][str(author.id)]['announcements'] = True
                save_guild_data(guild_id, guild_data)
                
                # The status defines the human readable status of the announcements to be displayed in the response.
                announcements_status = 'will be' if guild_data['features']['birthday']['birthdays'][str(author.id)]['announcements'] else 'will not be'
                await ctx.send_response(f'{author.mention} has set their birthday to {date} and {announcements_status} announced.',ephemeral=True)
        else:
            LOGGER.debug(f'{author.name} used /set_birthday {date} but the format is not correct.')
            await ctx.send_response('The date must is DAY/MONTH format.',ephemeral=True)

    @commands.slash_command(description='Enable or disable birthday announcements.')
    @option(name='enable',description='Enable birthday announcements.',required=True)
    @option(name='for_user',description='The user to enable or disable birthday announcements for.',required=False,type=discord.Member)
    async def birthday_announcements(self,ctx:discord.ApplicationContext, enable:bool, for_user:discord.Member):
        """Enable or disable birthday announcements."""
        command_name = 'birthday_announcements'
        guild_id = ctx.guild.id
        guild_data = get_guild_data(guild_id) or dict()
        author = ctx.author
        if for_user:
            if author.guild_permissions.administrator: # Check if author is an administrator in case they want to set the birthday for another user
                LOGGER.debug(f'{author.name} used /{command_name} {enable} for {for_user.name}.')
                guild_data['features']['birthday']['birthdays'][str(for_user.id)]['announcements'] = enable
                save_guild_data(guild_id, guild_data)
                await ctx.send_response(f'Announcements for {for_user.name} are set to {enable}',ephemeral=True)
            else:
                LOGGER.debug(f'{author.name} tried to use /{command_name} {enable} for {for_user.name} but is not an administrator.')
                await ctx.send_response('You must be an administrator to run the command with "for_user".',ephemeral=True)
        else:
            LOGGER.debug(f'{author.name} used /{command_name} {enable}.')
            guild_data['features']['birthday']['birthdays'][str(author.id)]['announcements'] = enable
            save_guild_data(guild_id, guild_data)
            await ctx.send_response(f'Your birthday announcements have been set to {enable}',ephemeral=True)

    @commands.slash_command(description='Sets the channel to send birthday announcements to.')
    @option(name='channel',description='The channel to send birthday announcements to.',required=True,type=discord.TextChannel)
    async def birthday_announcements_channel(self,ctx:discord.ApplicationContext, channel:discord.TextChannel):
        """Sets the channel to send birthday announcements to."""
        command_name = 'birthday_announcements_channel'
        guild_id = ctx.guild.id
        guild_data = get_guild_data(guild_id) or dict()
        author = ctx.author
        if author.guild_permissions.administrator:
            LOGGER.debug(f'{author.name} used /{command_name} {channel.name}.')
            guild_data['features']['birthday']['birthday_announcements_channel'] = channel.id
            save_guild_data(guild_id, guild_data)
            await ctx.send_response(f'Birthday announcements will be sent to {channel.mention}.',ephemeral=True)
        else:
            LOGGER.debug(f'{author.name} tried to use /{command_name} {channel.mention} but is not an administrator.')
            await ctx.send_response('You must be an administrator to run this command.',ephemeral=True)

