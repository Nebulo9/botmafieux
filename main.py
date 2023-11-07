import os, discord, logging
from dotenv import load_dotenv
from discord.ext import tasks
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s: %(name)s: %(message)s')
LOGGER = logging.getLogger('botmafieux')
LOGGER.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='botmafieux.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
LOGGER.addHandler(handler)

bot_intents = discord.Intents.default()
bot_intents.message_content = True
bot_intents.members = True
bot_intents.presences = True
bot_intents.guilds = True
bot_intents.reactions = True

bot = discord.Bot(command_prefix='$', intents=bot_intents)

@bot.slash_command(description="Test")
async def test(ctx:discord.ApplicationContext):
    user = ctx.author
    LOGGER.debug(f'{user.name} used /test.')
    await ctx.send_response('test',ephemeral=True)

@tasks.loop(time=datetime.time(datetime.strptime('00:00','%H:%M')))
async def test_loop():
    LOGGER.debug('test_loop')
    
@bot.event
async def on_ready():
    LOGGER.info(f'{bot.user.name} has connected to Discord!')
    LOGGER.debug(f'Guilds: {bot.guilds}')
    test_loop.start()

if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    bot.run(TOKEN)
    