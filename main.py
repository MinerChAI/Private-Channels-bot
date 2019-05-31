from discord.ext.commands import Bot
from const import TOKEN

bot = Bot('+')
bot.load_extension('ext.private_channels')
bot.load_extension('jishaku')


def run():
    bot.run(TOKEN)


if __name__ == '__main__':
    run()
