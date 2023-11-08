import discord
from ..cogs.birthday import BirthdayCog

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.members = True
bot_intents.presences = True
bot_intents.guilds = True
bot_intents.reactions = True

bot = discord.Bot(command_prefix='$', intents=bot_intents)

bot.add_cog(BirthdayCog(bot))