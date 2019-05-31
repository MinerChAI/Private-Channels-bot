from discord.ext.commands import Bot
from const import TOKEN

bot = Bot('+')
bot.load_extension('ext.private_channels')
bot.load_extension('jishaku')

bot.run(TOKEN)
