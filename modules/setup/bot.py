import discord
from ..cogs.birthday import BirthdayCog
from ..cogs.productivity import ProductivityCog
from .logger import LOGGER

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.members = True
bot_intents.presences = True
bot_intents.guilds = True
bot_intents.reactions = True

bot = discord.Bot(command_prefix='$', intents=bot_intents)

COGS = [BirthdayCog, ProductivityCog]

for cog in COGS:
    bot.add_cog(cog(bot))

def reload_feature(feature:str):
    LOGGER.debug(bot.cogs)
    LOGGER.debug(f'Reloading {feature}...')
    bot.remove_cog(feature.capitalize()+'Cog')
    cog = globals()[feature.capitalize()+'Cog']
    bot.add_cog(cog(bot))
    LOGGER.debug(f'{feature} reloaded!')
